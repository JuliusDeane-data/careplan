"""Automatische Dienstplanerstellung mit Google OR-Tools (CP-SAT).

Harte Bedingungen (werden nie verletzt):
- Qualifikationsanforderung des Dienstes
- Abwesenheiten (Urlaub, Krankheit, …)
- Ausgeschlossene Dienstarten und gesperrte Wochentage
- Max. ein Dienst pro Tag (auch standortübergreifend)
- Mindestens 11h Ruhezeit zwischen zwei Diensten (§5 ArbZG)
- Max. 60h in jedem 7-Tage-Fenster
- Max. aufeinanderfolgende Arbeitstage / Nachtdienste (pro Mitarbeiter)
- Monatssoll + erlaubte Mehrarbeit wird nicht überschritten
- Manuell fixierte ("gepinnte") Zuweisungen bleiben bestehen

Weiche Ziele (Optimierung, absteigende Priorität):
1. Möglichst keine unbesetzten Dienste
2. Plan-Stunden nah am vertraglichen Monatssoll
3. Bevorzugte Dienstarten belohnen
4. Wochenenddienste fair (proportional zum Stundensoll) verteilen
5. Mindestens ein komplett freies Wochenende pro Mitarbeiter
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from ortools.sat.python import cp_model

from app.scheduling import rules


@dataclass(frozen=True)
class SlotSpec:
    """Ein zu besetzender Dienst an einem Tag."""

    day: date
    template_id: int
    start_minutes: int      # Minuten seit Mitternacht
    duration_minutes: int
    is_night: bool
    staff_needed: int
    required_qualification_id: int | None


@dataclass
class EmployeeSpec:
    employee_id: int
    name: str
    qualification_ids: set[int]
    monthly_target_minutes: int
    pref_day: str            # BEVORZUGT / NEUTRAL / AUSGESCHLOSSEN
    pref_night: str
    blocked_weekdays: set[int]
    max_consecutive_days: int
    max_consecutive_nights: int
    absences: list[tuple[date, date]] = field(default_factory=list)
    # Bereits feststehende Dienste (andere Standorte, Nachbarmonate):
    # (Tag, Startminute, Dauer, ist_nacht)
    external_shifts: list[tuple[date, int, int, bool]] = field(default_factory=list)
    # Im Planungsmonat an anderen Standorten bereits verplante Minuten.
    external_month_minutes: int = 0


@dataclass
class SolveResult:
    status: str
    feasible: bool
    # (Tag, template_id, employee_id)
    assignments: list[tuple[date, int, int]] = field(default_factory=list)
    # (Tag, template_id, Anzahl unbesetzter Plätze)
    unfilled: list[tuple[date, int, int]] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def _shift_interval(day: date, start_minutes: int, duration_minutes: int):
    """(Start, Ende) als Minuten-Offsets relativ zu einem Referenzdatum."""
    return start_minutes, start_minutes + duration_minutes


def _is_absent(emp: EmployeeSpec, day: date) -> bool:
    return any(a <= day <= b for a, b in emp.absences)


def _category_excluded(emp: EmployeeSpec, is_night: bool) -> bool:
    pref = emp.pref_night if is_night else emp.pref_day
    return pref == "AUSGESCHLOSSEN"


def _category_preferred(emp: EmployeeSpec, is_night: bool) -> bool:
    pref = emp.pref_night if is_night else emp.pref_day
    return pref == "BEVORZUGT"


def solve_schedule(
    days: list[date],
    slots: list[SlotSpec],
    employees: list[EmployeeSpec],
    pinned: list[tuple[date, int, int]] | None = None,
    time_limit_seconds: float = 15.0,
) -> SolveResult:
    """Erzeugt eine optimierte Dienstplan-Belegung für einen Monat.

    `slots` enthält je (Tag, Dienstart) genau einen Eintrag mit dem
    Personalbedarf. `pinned` fixiert vorhandene Zuweisungen.
    """
    pinned = pinned or []
    model = cp_model.CpModel()
    ref = min(days)

    def abs_minutes(day: date, minute_of_day: int) -> int:
        return (day - ref).days * 24 * 60 + minute_of_day

    emp_by_id = {e.employee_id: e for e in employees}
    slot_key = {(s.day, s.template_id): s for s in slots}

    # Entscheidungsvariablen nur für zulässige Kombinationen.
    x: dict[tuple[date, int, int], cp_model.IntVar] = {}
    for s in slots:
        for e in employees:
            if _is_absent(e, s.day):
                continue
            if s.day.weekday() in e.blocked_weekdays:
                continue
            if _category_excluded(e, s.is_night):
                continue
            if s.required_qualification_id is not None \
                    and s.required_qualification_id not in e.qualification_ids:
                continue
            # Tage mit externem Dienst sind komplett blockiert.
            if any(d == s.day for d, *_ in e.external_shifts):
                continue
            x[(s.day, s.template_id, e.employee_id)] = model.NewBoolVar(
                f"x_{s.day.isoformat()}_{s.template_id}_{e.employee_id}"
            )

    # Gepinnte Zuweisungen fixieren (sofern Variable existiert; sonst ist die
    # Pinnung regelwidrig und wird in der Validierung gemeldet).
    for day, template_id, employee_id in pinned:
        var = x.get((day, template_id, employee_id))
        if var is not None:
            model.Add(var == 1)

    # Besetzung: Anzahl Zuweisungen + Fehlbesetzung == Bedarf.
    shortfalls: dict[tuple[date, int], cp_model.IntVar] = {}
    for s in slots:
        vars_for_slot = [
            x[(s.day, s.template_id, e.employee_id)]
            for e in employees
            if (s.day, s.template_id, e.employee_id) in x
        ]
        short = model.NewIntVar(0, s.staff_needed, f"short_{s.day}_{s.template_id}")
        shortfalls[(s.day, s.template_id)] = short
        model.Add(sum(vars_for_slot) + short == s.staff_needed)

    objective_terms = []

    # Max. ein Dienst pro Tag.
    for e in employees:
        for day in days:
            day_vars = [
                x[(day, s.template_id, e.employee_id)]
                for s in slots
                if s.day == day and (day, s.template_id, e.employee_id) in x
            ]
            if len(day_vars) > 1:
                model.Add(sum(day_vars) <= 1)

    # Ruhezeit: unverträgliche Dienst-Paare an benachbarten Tagen ausschließen.
    # Auch gegen externe (feststehende) Dienste.
    min_rest = rules.MIN_REST_HOURS * 60
    slots_by_day: dict[date, list[SlotSpec]] = {}
    for s in slots:
        slots_by_day.setdefault(s.day, []).append(s)

    for e in employees:
        for day in days:
            for offset in (1, 2):
                other_day = day + timedelta(days=offset)
                if other_day not in slots_by_day:
                    continue
                for s1 in slots_by_day.get(day, []):
                    v1 = x.get((day, s1.template_id, e.employee_id))
                    if v1 is None:
                        continue
                    end1 = abs_minutes(day, s1.start_minutes + s1.duration_minutes)
                    for s2 in slots_by_day[other_day]:
                        v2 = x.get((other_day, s2.template_id, e.employee_id))
                        if v2 is None:
                            continue
                        start2 = abs_minutes(other_day, s2.start_minutes)
                        if start2 - end1 < min_rest:
                            model.Add(v1 + v2 <= 1)

        # Ruhezeit gegenüber externen Diensten.
        for ext_day, ext_start, ext_dur, _night in e.external_shifts:
            ext_s = abs_minutes(ext_day, ext_start) if min(days) <= ext_day <= max(days) \
                else (ext_day - ref).days * 24 * 60 + ext_start
            ext_e = ext_s + ext_dur
            for day in days:
                if abs((day - ext_day).days) > 2:
                    continue
                for s1 in slots_by_day.get(day, []):
                    v1 = x.get((day, s1.template_id, e.employee_id))
                    if v1 is None:
                        continue
                    s_start = abs_minutes(day, s1.start_minutes)
                    s_end = s_start + s1.duration_minutes
                    if (s_start - ext_e < min_rest and s_start >= ext_s) or \
                       (ext_s - s_end < min_rest and ext_s >= s_start):
                        model.Add(v1 == 0)

    # Hilfsvariablen: arbeitet an Tag d / Nachtdienst an Tag d.
    works: dict[tuple[int, date], cp_model.IntVar] = {}
    night_works: dict[tuple[int, date], cp_model.IntVar] = {}
    horizon_start = min(days) - timedelta(days=7)
    horizon_end = max(days) + timedelta(days=7)
    horizon = [horizon_start + timedelta(days=i)
               for i in range((horizon_end - horizon_start).days + 1)]

    for e in employees:
        ext_days = {d for d, *_ in e.external_shifts}
        ext_night_days = {d for d, _s, _du, night in e.external_shifts if night}
        for day in horizon:
            day_vars = [
                x[(day, s.template_id, e.employee_id)]
                for s in slots_by_day.get(day, [])
                if (day, s.template_id, e.employee_id) in x
            ]
            night_vars = [
                x[(day, s.template_id, e.employee_id)]
                for s in slots_by_day.get(day, [])
                if s.is_night and (day, s.template_id, e.employee_id) in x
            ]
            if day in ext_days:
                works[(e.employee_id, day)] = model.NewConstant(1)
            elif day_vars:
                w = model.NewBoolVar(f"w_{e.employee_id}_{day}")
                model.AddMaxEquality(w, day_vars)
                works[(e.employee_id, day)] = w
            else:
                works[(e.employee_id, day)] = model.NewConstant(0)

            if day in ext_night_days:
                night_works[(e.employee_id, day)] = model.NewConstant(1)
            elif night_vars:
                nw = model.NewBoolVar(f"nw_{e.employee_id}_{day}")
                model.AddMaxEquality(nw, night_vars)
                night_works[(e.employee_id, day)] = nw
            else:
                night_works[(e.employee_id, day)] = model.NewConstant(0)

    # Max. aufeinanderfolgende Arbeitstage / Nächte (gleitende Fenster).
    for e in employees:
        n = e.max_consecutive_days
        for i in range(len(horizon) - n):
            window = horizon[i:i + n + 1]
            model.Add(sum(works[(e.employee_id, d)] for d in window) <= n)
        m = e.max_consecutive_nights
        for i in range(len(horizon) - m):
            window = horizon[i:i + m + 1]
            model.Add(sum(night_works[(e.employee_id, d)] for d in window) <= m)

    # Max. Stunden in jedem 7-Tage-Fenster (inkl. externer Dienste).
    # Hart: 60h-Spitzengrenze. Weich: Überschreitung des 48h-Durchschnitts
    # wird bestraft, damit Dienste gleichmäßig verteilt werden.
    week_cap = rules.MAX_HOURS_PER_7_DAYS * 60
    week_soft = rules.AVG_MAX_HOURS_PER_7_DAYS * 60
    for e in employees:
        ext_min_by_day = {}
        for d, _s, dur, _n in e.external_shifts:
            ext_min_by_day[d] = ext_min_by_day.get(d, 0) + dur
        for i in range(len(horizon) - 6):
            window = horizon[i:i + 7]
            terms = []
            fixed = 0
            for day in window:
                fixed += ext_min_by_day.get(day, 0)
                for s in slots_by_day.get(day, []):
                    v = x.get((day, s.template_id, e.employee_id))
                    if v is not None:
                        terms.append(s.duration_minutes * v)
            if terms:
                model.Add(sum(terms) + fixed <= week_cap)
                excess = model.NewIntVar(0, week_cap - week_soft,
                                         f"wkx_{e.employee_id}_{i}")
                model.Add(excess >= sum(terms) + fixed - week_soft)
                objective_terms.append(3 * excess)

    # Monatsstunden: harte Obergrenze + weiche Annäherung ans Soll.
    for e in employees:
        terms = []
        for s in slots:
            v = x.get((s.day, s.template_id, e.employee_id))
            if v is not None:
                terms.append(s.duration_minutes * v)
        total = model.NewIntVar(0, 24 * 60 * len(days), f"tot_{e.employee_id}")
        model.Add(total == sum(terms) + e.external_month_minutes)
        cap = e.monthly_target_minutes + rules.MAX_MONTHLY_OVERTIME_MINUTES
        model.Add(total <= cap)
        dev = model.NewIntVar(0, 24 * 60 * len(days), f"dev_{e.employee_id}")
        model.Add(dev >= total - e.monthly_target_minutes)
        model.Add(dev >= e.monthly_target_minutes - total)
        # Gewicht 1 pro Minute Abweichung vom Soll.
        objective_terms.append(dev)

    # Fehlbesetzungen dominieren alles andere.
    for short in shortfalls.values():
        objective_terms.append(100_000 * short)

    # Bevorzugte Dienstarten belohnen.
    for (day, template_id, employee_id), v in x.items():
        s = slot_key[(day, template_id)]
        e = emp_by_id[employee_id]
        if _category_preferred(e, s.is_night):
            objective_terms.append(-90 * v)

    # Wochenend-Fairness: Abweichung vom proportionalen Anteil bestrafen.
    weekend_days = [d for d in days if d.weekday() >= 5]
    total_weekend_slots = sum(
        s.staff_needed for s in slots if s.day.weekday() >= 5
    )
    total_target = sum(e.monthly_target_minutes for e in employees) or 1
    for e in employees:
        we_vars = [
            x[(d, s.template_id, e.employee_id)]
            for d in weekend_days
            for s in slots_by_day.get(d, [])
            if (d, s.template_id, e.employee_id) in x
        ]
        if not we_vars:
            continue
        share = round(total_weekend_slots * e.monthly_target_minutes / total_target)
        count = model.NewIntVar(0, len(we_vars), f"we_{e.employee_id}")
        model.Add(count == sum(we_vars))
        wdev = model.NewIntVar(0, len(we_vars) + share, f"wedev_{e.employee_id}")
        model.Add(wdev >= count - share)
        model.Add(wdev >= share - count)
        objective_terms.append(120 * wdev)

    # Mindestens ein komplett freies Wochenende (weich).
    saturdays = [d for d in days if d.weekday() == 5 and d + timedelta(days=1) in days]
    for e in employees:
        if not saturdays:
            continue
        free_we_vars = []
        for sat in saturdays:
            sun = sat + timedelta(days=1)
            free = model.NewBoolVar(f"freewe_{e.employee_id}_{sat}")
            model.Add(works[(e.employee_id, sat)] + works[(e.employee_id, sun)] == 0) \
                .OnlyEnforceIf(free)
            free_we_vars.append(free)
        has_free = model.NewBoolVar(f"hasfreewe_{e.employee_id}")
        model.AddMaxEquality(has_free, free_we_vars)
        objective_terms.append(800 * (1 - has_free))

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_workers = 8
    status = solver.Solve(model)

    status_name = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return SolveResult(status=status_name, feasible=False)

    assignments = [
        (day, template_id, employee_id)
        for (day, template_id, employee_id), v in x.items()
        if solver.Value(v) == 1
    ]
    unfilled = [
        (day, template_id, solver.Value(short))
        for (day, template_id), short in shortfalls.items()
        if solver.Value(short) > 0
    ]
    return SolveResult(
        status=status_name,
        feasible=True,
        assignments=sorted(assignments),
        unfilled=sorted(unfilled),
        stats={
            "objective": solver.ObjectiveValue(),
            "wall_time": round(solver.WallTime(), 2),
            "num_variables": len(x),
        },
    )
