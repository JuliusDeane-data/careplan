"""Tests für das Arbeitszeit-Regelwerk."""
from datetime import date, time

from app.scheduling import rules
from app.scheduling.rules import EmployeeRules, make_shift_info


def day_shift(d: date, name="Tagdienst"):
    return make_shift_info(d, time(8, 0), time(20, 0), is_night=False, shift_name=name)


def night_shift(d: date, name="Nachtdienst"):
    return make_shift_info(d, time(20, 0), time(8, 0), is_night=True, shift_name=name)


def basic_rules(**kwargs) -> EmployeeRules:
    defaults = dict(employee_id=1, name="Test Person")
    defaults.update(kwargs)
    return EmployeeRules(**defaults)


def codes(violations, severity=None):
    return {v.code for v in violations if severity is None or v.severity == severity}


def test_no_violations_for_clean_schedule():
    shifts = [day_shift(date(2026, 7, d)) for d in (1, 2, 3, 10, 11)]
    violations = rules.find_violations(basic_rules(), shifts, month=(2026, 7))
    assert codes(violations, "ERROR") == set()


def test_rest_violation_night_then_day():
    # Nachtdienst endet 02.07. 08:00, Tagdienst beginnt 02.07. 08:00 -> 0h Ruhe.
    shifts = [night_shift(date(2026, 7, 1)), day_shift(date(2026, 7, 2))]
    violations = rules.find_violations(basic_rules(), shifts)
    assert "RUHEZEIT" in codes(violations, "ERROR")


def test_night_to_night_is_allowed():
    # Nacht endet 08:00, nächste Nacht beginnt 20:00 -> 12h Ruhe, zulässig.
    shifts = [night_shift(date(2026, 7, 1)), night_shift(date(2026, 7, 2))]
    violations = rules.find_violations(basic_rules(), shifts)
    assert "RUHEZEIT" not in codes(violations)


def test_double_booking_same_day():
    shifts = [day_shift(date(2026, 7, 1)), night_shift(date(2026, 7, 1))]
    violations = rules.find_violations(basic_rules(), shifts)
    assert "DOPPELBELEGUNG" in codes(violations, "ERROR")


def test_too_many_consecutive_days():
    shifts = [day_shift(date(2026, 7, d)) for d in range(1, 8)]  # 7 Tage in Folge
    violations = rules.find_violations(basic_rules(max_consecutive_days=6), shifts)
    assert "FOLGETAGE" in codes(violations, "ERROR")


def test_consecutive_days_at_limit_ok():
    shifts = [day_shift(date(2026, 7, d)) for d in range(1, 7)]  # genau 6
    violations = rules.find_violations(basic_rules(max_consecutive_days=6), shifts)
    assert "FOLGETAGE" not in codes(violations)


def test_too_many_consecutive_nights():
    shifts = [night_shift(date(2026, 7, d)) for d in range(1, 6)]  # 5 Nächte
    violations = rules.find_violations(basic_rules(max_consecutive_nights=4), shifts)
    assert "FOLGENAECHTE" in codes(violations, "ERROR")


def test_absence_conflict():
    shifts = [day_shift(date(2026, 7, 10))]
    violations = rules.find_violations(
        basic_rules(absences=[(date(2026, 7, 8), date(2026, 7, 12))]), shifts
    )
    assert "ABWESENHEIT" in codes(violations, "ERROR")


def test_excluded_night_shift():
    shifts = [night_shift(date(2026, 7, 1))]
    violations = rules.find_violations(basic_rules(night_excluded=True), shifts)
    assert "DIENSTART" in codes(violations, "ERROR")


def test_blocked_weekday():
    # 06.07.2026 ist ein Montag (weekday 0).
    shifts = [day_shift(date(2026, 7, 6))]
    violations = rules.find_violations(basic_rules(blocked_weekdays={0}), shifts)
    assert "WOCHENTAG" in codes(violations, "ERROR")


def test_weekly_hours_hard_limit():
    # 6 x 12h = 72h in 7 Tagen -> harter Verstoß (> 60h).
    shifts = [day_shift(date(2026, 7, d)) for d in range(1, 7)]
    violations = rules.find_violations(basic_rules(), shifts)
    assert "WOCHENSTUNDEN" in codes(violations, "ERROR")


def test_weekly_hours_warn_between_48_and_60():
    # 5 x 12h = 60h in 7 Tagen -> keine harte Grenze, aber Warnung (> 48h).
    shifts = [day_shift(date(2026, 7, d)) for d in (1, 2, 3, 4, 5)]
    violations = rules.find_violations(basic_rules(max_consecutive_days=6), shifts)
    weekly = [v for v in violations if v.code == "WOCHENSTUNDEN"]
    assert weekly and all(v.severity == "WARN" for v in weekly)


def test_monthly_overtime():
    target = 100 * 60  # 100h Soll
    shifts = [day_shift(date(2026, 7, d)) for d in range(1, 31, 3)]  # 10 Dienste
    # 120h geplant, Soll 100h, erlaubte Mehrarbeit 12h -> Verstoß.
    violations = rules.find_violations(
        basic_rules(monthly_target_minutes=target), shifts, month=(2026, 7)
    )
    assert "MONATSSTUNDEN" in codes(violations, "ERROR")


def test_free_weekend_warning():
    # Jedes Wochenende mindestens ein Dienst -> Warnung.
    shifts = []
    d = date(2026, 7, 1)
    while d.month == 7:
        if d.weekday() == 5:
            shifts.append(day_shift(d))
        d = d.replace(day=d.day + 1) if d.day < 31 else date(2026, 8, 1)
    violations = rules.find_violations(basic_rules(), shifts, month=(2026, 7))
    assert "FREIES_WOCHENENDE" in codes(violations, "WARN")
