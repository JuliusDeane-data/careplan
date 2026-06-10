"""Arbeitsrechtliche Regeln für die Dienstplanung von Pflegekräften.

Grundlage ist das Arbeitszeitgesetz (ArbZG) und die EU-Arbeitszeitrichtlinie:

- §5 ArbZG: mindestens 11 Stunden ununterbrochene Ruhezeit zwischen zwei
  Diensten (in Pflegeeinrichtungen mit Ausgleich auf 10h verkürzbar –
  hier wird konservativ 11h erzwungen).
- §3 ArbZG / EU-RL: durchschnittlich max. 48 Wochenstunden; in der Spitze
  max. 60 Stunden in 7 Tagen, wenn ein Ausgleich erfolgt. 12-Stunden-
  Dienste sind in der außerklinischen Intensivpflege über tarifliche
  Öffnungsklauseln (§7 ArbZG) üblich.
- Max. 6 Arbeitstage in Folge (übliche tarifliche Obergrenze, pro
  Mitarbeiter weiter einschränkbar).
- Max. 4 Nachtdienste in Folge (arbeitsmedizinische Empfehlung §6 ArbZG,
  pro Mitarbeiter einstellbar).
- Monatliches Stundenkonto: Plan-Stunden dürfen das Vertragssoll nur um
  eine begrenzte Mehrarbeit überschreiten.

Diese Datei ist die einzige Quelle für die Grenzwerte; Solver und
Plan-Validierung verwenden dieselben Konstanten.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

# Harte Grenzwerte
MIN_REST_HOURS = 11
MAX_HOURS_PER_7_DAYS = 60          # harte Spitzengrenze (mit Ausgleich)
AVG_MAX_HOURS_PER_7_DAYS = 48      # Richtwert -> Warnung bei Überschreitung
MAX_SHIFT_HOURS = 12               # längster zulässiger Einzeldienst
DEFAULT_MAX_CONSECUTIVE_DAYS = 6
DEFAULT_MAX_CONSECUTIVE_NIGHTS = 4
MAX_MONTHLY_OVERTIME_MINUTES = 12 * 60  # zulässige Mehrarbeit über Monatssoll

ERROR = "ERROR"
WARN = "WARN"


@dataclass(frozen=True)
class ShiftInfo:
    """Ein konkreter Dienst eines Mitarbeiters (planübergreifend)."""

    day: date
    start: datetime
    end: datetime
    is_night: bool
    location_name: str = ""
    shift_name: str = ""

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass
class Violation:
    employee_id: int
    employee_name: str
    day: date
    code: str
    severity: str
    message: str


@dataclass
class EmployeeRules:
    """Für die Prüfung relevante Stammdaten eines Mitarbeiters."""

    employee_id: int
    name: str
    max_consecutive_days: int = DEFAULT_MAX_CONSECUTIVE_DAYS
    max_consecutive_nights: int = DEFAULT_MAX_CONSECUTIVE_NIGHTS
    blocked_weekdays: set[int] = field(default_factory=set)
    night_excluded: bool = False
    day_excluded: bool = False
    # Abwesenheiten als Liste von (von, bis) einschließlich.
    absences: list[tuple[date, date]] = field(default_factory=list)
    monthly_target_minutes: int | None = None


def make_shift_info(day: date, start_time: time, end_time: time, is_night: bool,
                    location_name: str = "", shift_name: str = "") -> ShiftInfo:
    start = datetime.combine(day, start_time)
    end = datetime.combine(day, end_time)
    if end <= start:
        end += timedelta(days=1)
    return ShiftInfo(day=day, start=start, end=end, is_night=is_night,
                     location_name=location_name, shift_name=shift_name)


def rest_conflict(a: ShiftInfo, b: ShiftInfo, min_rest_hours: float = MIN_REST_HOURS) -> bool:
    """True, wenn zwischen zwei Diensten weniger als die Mindestruhezeit liegt
    (oder sie sich überschneiden)."""
    first, second = (a, b) if a.start <= b.start else (b, a)
    return (second.start - first.end) < timedelta(hours=min_rest_hours)


def find_violations(rules: EmployeeRules, shifts: list[ShiftInfo],
                    month: tuple[int, int] | None = None) -> list[Violation]:
    """Prüft alle Dienste eines Mitarbeiters (idealerweise inkl. Diensten in
    angrenzenden Monaten und an anderen Standorten) gegen die Regeln.

    `month` (Jahr, Monat) begrenzt Stundenkonto-Prüfungen auf diesen Monat.
    """
    out: list[Violation] = []
    shifts = sorted(shifts, key=lambda s: s.start)

    def add(day: date, code: str, severity: str, message: str):
        out.append(Violation(rules.employee_id, rules.name, day, code, severity, message))

    # Doppelbelegung am selben Tag
    by_day: dict[date, list[ShiftInfo]] = {}
    for s in shifts:
        by_day.setdefault(s.day, []).append(s)
    def shift_label(s: ShiftInfo) -> str:
        if s.shift_name and s.location_name:
            return f"{s.shift_name} ({s.location_name})"
        return s.shift_name or s.location_name or "Dienst"

    for day, items in by_day.items():
        if len(items) > 1:
            add(day, "DOPPELBELEGUNG", ERROR,
                f"Mehrere Dienste am {day.strftime('%d.%m.%Y')} "
                f"({', '.join(shift_label(i) for i in items)}).")

    # Einzeldienstlänge
    for s in shifts:
        if s.minutes > MAX_SHIFT_HOURS * 60:
            add(s.day, "DIENSTLAENGE", ERROR,
                f"Dienst am {s.day.strftime('%d.%m.%Y')} ist länger als "
                f"{MAX_SHIFT_HOURS} Stunden.")

    # Ruhezeit zwischen aufeinanderfolgenden Diensten
    for prev, nxt in zip(shifts, shifts[1:]):
        if prev.day == nxt.day:
            continue  # bereits als Doppelbelegung gemeldet
        if rest_conflict(prev, nxt):
            rest = (nxt.start - prev.end).total_seconds() / 3600
            add(nxt.day, "RUHEZEIT", ERROR,
                f"Nur {max(rest, 0):.1f}h Ruhezeit vor dem Dienst am "
                f"{nxt.day.strftime('%d.%m.%Y')} (mind. {MIN_REST_HOURS}h, §5 ArbZG).")

    # Abwesenheiten
    for s in shifts:
        for a_from, a_to in rules.absences:
            if a_from <= s.day <= a_to:
                add(s.day, "ABWESENHEIT", ERROR,
                    f"Dienst am {s.day.strftime('%d.%m.%Y')} fällt in eine "
                    f"Abwesenheit ({a_from.strftime('%d.%m.')}–{a_to.strftime('%d.%m.%Y')}).")

    # Ausgeschlossene Dienstarten / gesperrte Wochentage
    for s in shifts:
        if s.is_night and rules.night_excluded:
            add(s.day, "DIENSTART", ERROR,
                f"Nachtdienst am {s.day.strftime('%d.%m.%Y')}, obwohl Nachtdienste "
                f"ausgeschlossen sind.")
        if not s.is_night and rules.day_excluded:
            add(s.day, "DIENSTART", ERROR,
                f"Tagdienst am {s.day.strftime('%d.%m.%Y')}, obwohl Tagdienste "
                f"ausgeschlossen sind.")
        if s.day.weekday() in rules.blocked_weekdays:
            wd = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                  "Freitag", "Samstag", "Sonntag"][s.day.weekday()]
            add(s.day, "WOCHENTAG", ERROR,
                f"Dienst am {s.day.strftime('%d.%m.%Y')} ({wd}), obwohl dieser "
                f"Wochentag gesperrt ist.")

    # Aufeinanderfolgende Arbeitstage
    work_days = set(by_day.keys())
    sorted_days = sorted(work_days)
    run_start = None
    prev_d = None
    for d in sorted_days + [None]:
        if d is not None and (prev_d is None or d != prev_d + timedelta(days=1)):
            run_start = d
        if prev_d is not None and (d is None or d != prev_d + timedelta(days=1)):
            run_len = (prev_d - run_start).days + 1
            if run_len > rules.max_consecutive_days:
                add(prev_d, "FOLGETAGE", ERROR,
                    f"{run_len} Arbeitstage in Folge bis {prev_d.strftime('%d.%m.%Y')} "
                    f"(max. {rules.max_consecutive_days}).")
        prev_d = d

    # Aufeinanderfolgende Nachtdienste
    night_days = {s.day for s in shifts if s.is_night}
    sorted_nights = sorted(night_days)
    run_start = None
    prev_d = None
    for d in sorted_nights + [None]:
        if d is not None and (prev_d is None or d != prev_d + timedelta(days=1)):
            run_start = d
        if prev_d is not None and (d is None or d != prev_d + timedelta(days=1)):
            run_len = (prev_d - run_start).days + 1
            if run_len > rules.max_consecutive_nights:
                add(prev_d, "FOLGENAECHTE", ERROR,
                    f"{run_len} Nachtdienste in Folge bis {prev_d.strftime('%d.%m.%Y')} "
                    f"(max. {rules.max_consecutive_nights}).")
        prev_d = d

    # Stunden in beliebigen 7-Tage-Fenstern. Überlappende auffällige Fenster
    # werden zu einer Meldung pro zusammenhängendem Zeitraum zusammengefasst.
    if shifts:
        first, last = shifts[0].day, shifts[-1].day
        flagged: list[tuple[date, date, int, str]] = []  # (von, bis, Minuten, Schwere)
        d = first
        while d <= last:
            window_end = d + timedelta(days=6)
            minutes = sum(s.minutes for s in shifts if d <= s.day <= window_end)
            if minutes > MAX_HOURS_PER_7_DAYS * 60:
                flagged.append((d, window_end, minutes, ERROR))
            elif minutes > AVG_MAX_HOURS_PER_7_DAYS * 60:
                flagged.append((d, window_end, minutes, WARN))
            d += timedelta(days=1)

        merged: list[list] = []
        for start, end, minutes, severity in flagged:
            if merged and merged[-1][3] == severity \
                    and start <= merged[-1][1] + timedelta(days=1):
                merged[-1][1] = end
                merged[-1][2] = max(merged[-1][2], minutes)
            else:
                merged.append([start, end, minutes, severity])
        for start, end, minutes, severity in merged:
            if severity == ERROR:
                add(end, "WOCHENSTUNDEN", ERROR,
                    f"Bis zu {minutes / 60:.0f}h innerhalb von 7 Tagen "
                    f"({start.strftime('%d.%m.')}–{end.strftime('%d.%m.%Y')}, "
                    f"max. {MAX_HOURS_PER_7_DAYS}h).")
            else:
                add(end, "WOCHENSTUNDEN", WARN,
                    f"Bis zu {minutes / 60:.0f}h innerhalb von 7 Tagen "
                    f"({start.strftime('%d.%m.')}–{end.strftime('%d.%m.%Y')}) – über dem "
                    f"48h-Durchschnitt, Ausgleich erforderlich.")

    # Monatliches Stundenkonto
    if month and rules.monthly_target_minutes is not None:
        year, mon = month
        month_minutes = sum(s.minutes for s in shifts
                            if s.day.year == year and s.day.month == mon)
        if month_minutes > rules.monthly_target_minutes + MAX_MONTHLY_OVERTIME_MINUTES:
            add(date(year, mon, 1), "MONATSSTUNDEN", ERROR,
                f"{month_minutes / 60:.1f}h geplant bei einem Monatssoll von "
                f"{rules.monthly_target_minutes / 60:.1f}h "
                f"(max. +{MAX_MONTHLY_OVERTIME_MINUTES / 60:.0f}h Mehrarbeit).")

    # Mindestens ein komplett freies Wochenende im Monat (Empfehlung)
    if month:
        year, mon = month
        import calendar

        weekends = []
        for dnum in range(1, calendar.monthrange(year, mon)[1] + 1):
            d0 = date(year, mon, dnum)
            if d0.weekday() == 5:  # Samstag
                weekends.append((d0, d0 + timedelta(days=1)))
        month_work = {s.day for s in shifts}
        if weekends and all(sa in month_work or so in month_work for sa, so in weekends):
            add(date(year, mon, 1), "FREIES_WOCHENENDE", WARN,
                "Kein komplett freies Wochenende in diesem Monat.")

    return out
