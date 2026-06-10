"""Tests für den CP-SAT-Dienstplan-Solver: erzeugte Pläne müssen alle harten
Arbeitszeitregeln einhalten."""
from datetime import date, time, timedelta

from app.scheduling import rules
from app.scheduling.solver import EmployeeSpec, SlotSpec, solve_schedule

DAY_START = 8 * 60
NIGHT_START = 20 * 60
TWELVE_H = 12 * 60

JULY_2026 = [date(2026, 7, d) for d in range(1, 32)]


def make_slots(days, day_staff=1, night_staff=1, required_qual=None):
    slots = []
    for d in days:
        slots.append(SlotSpec(day=d, template_id=1, start_minutes=DAY_START,
                              duration_minutes=TWELVE_H, is_night=False,
                              staff_needed=day_staff,
                              required_qualification_id=required_qual))
        slots.append(SlotSpec(day=d, template_id=2, start_minutes=NIGHT_START,
                              duration_minutes=TWELVE_H, is_night=True,
                              staff_needed=night_staff,
                              required_qualification_id=required_qual))
    return slots


def make_employee(emp_id, hours=40.0, quals=None, **kwargs):
    target = round(hours * len(JULY_2026) / 7 * 60)
    defaults = dict(
        employee_id=emp_id, name=f"MA {emp_id}",
        qualification_ids=quals or {1},
        monthly_target_minutes=target,
        pref_day="NEUTRAL", pref_night="NEUTRAL",
        blocked_weekdays=set(), max_consecutive_days=6,
        max_consecutive_nights=4,
    )
    defaults.update(kwargs)
    return EmployeeSpec(**defaults)


def validate(result, employees):
    """Führt das Regelwerk über das Solver-Ergebnis aus; gibt harte Verstöße zurück."""
    errors = []
    for e in employees:
        shifts = []
        for day, template_id, emp_id in result.assignments:
            if emp_id != e.employee_id:
                continue
            start = time(8, 0) if template_id == 1 else time(20, 0)
            end = time(20, 0) if template_id == 1 else time(8, 0)
            shifts.append(rules.make_shift_info(day, start, end,
                                                is_night=template_id == 2))
        emp_rules = rules.EmployeeRules(
            employee_id=e.employee_id, name=e.name,
            max_consecutive_days=e.max_consecutive_days,
            max_consecutive_nights=e.max_consecutive_nights,
            blocked_weekdays=e.blocked_weekdays,
            night_excluded=e.pref_night == "AUSGESCHLOSSEN",
            day_excluded=e.pref_day == "AUSGESCHLOSSEN",
            absences=e.absences,
            monthly_target_minutes=e.monthly_target_minutes,
        )
        violations = rules.find_violations(emp_rules, shifts, month=(2026, 7))
        errors.extend(v for v in violations if v.severity == "ERROR")
    return errors


def test_full_coverage_with_enough_staff():
    slots = make_slots(JULY_2026)
    employees = [make_employee(i) for i in range(1, 7)]  # 6 Vollzeitkräfte
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    assert result.unfilled == [], "Mit 6 Vollzeitkräften müssen 62 Dienste besetzbar sein"
    assert validate(result, employees) == []


def test_generated_plan_respects_all_hard_rules():
    slots = make_slots(JULY_2026, day_staff=2, night_staff=1)
    employees = [make_employee(i) for i in range(1, 10)]
    employees[0] = make_employee(1, pref_night="AUSGESCHLOSSEN")
    employees[1] = make_employee(2, blocked_weekdays={0, 1})
    employees[2] = make_employee(3, hours=20.0)
    employees[3] = make_employee(
        4, absences=[(date(2026, 7, 6), date(2026, 7, 17))])
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=25)
    assert result.feasible
    assert validate(result, employees) == []


def test_absences_are_respected():
    slots = make_slots(JULY_2026)
    vacation = (date(2026, 7, 1), date(2026, 7, 31))
    employees = [
        make_employee(1, absences=[vacation]),
        make_employee(2), make_employee(3), make_employee(4),
        make_employee(5), make_employee(6), make_employee(7),
    ]
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    assert all(emp_id != 1 for _, _, emp_id in result.assignments)


def test_excluded_night_shift_never_assigned():
    slots = make_slots(JULY_2026)
    employees = [make_employee(1, pref_night="AUSGESCHLOSSEN")] + \
                [make_employee(i) for i in range(2, 8)]
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    night_assignments = [(d, t, e) for d, t, e in result.assignments
                         if t == 2 and e == 1]
    assert night_assignments == []


def test_qualification_requirement():
    slots = make_slots(JULY_2026, required_qual=99)
    qualified = [make_employee(i, quals={1, 99}) for i in range(1, 7)]
    unqualified = make_employee(7, quals={1})
    employees = qualified + [unqualified]
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    assert all(emp_id != 7 for _, _, emp_id in result.assignments)


def test_pinned_assignments_are_kept():
    slots = make_slots(JULY_2026)
    employees = [make_employee(i) for i in range(1, 7)]
    pinned = [(date(2026, 7, 10), 1, 3), (date(2026, 7, 11), 2, 4)]
    result = solve_schedule(JULY_2026, slots, employees, pinned=pinned,
                            time_limit_seconds=20)
    assert result.feasible
    for p in pinned:
        assert p in result.assignments


def test_understaffing_reported_not_violated():
    """Mit zu wenig Personal bleiben Dienste offen, statt Regeln zu brechen."""
    slots = make_slots(JULY_2026)
    employees = [make_employee(1), make_employee(2)]  # 2 Personen, 62 Dienste
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    assert sum(n for _, _, n in result.unfilled) > 0
    assert validate(result, employees) == []


def test_external_shifts_block_same_day_and_rest():
    """Dienste an anderen Standorten blockieren den Tag und die Ruhezeit."""
    slots = make_slots(JULY_2026)
    # Externe Nachtdienste 09./10.07. an anderem Standort (endet 08:00 Folgetag).
    external = [
        (date(2026, 7, 9), NIGHT_START, TWELVE_H, True),
        (date(2026, 7, 10), NIGHT_START, TWELVE_H, True),
    ]
    employees = [make_employee(1, external_shifts=external,
                               external_month_minutes=2 * TWELVE_H)] + \
                [make_employee(i) for i in range(2, 8)]
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    emp1_days = {d for d, _, e in result.assignments if e == 1}
    assert date(2026, 7, 9) not in emp1_days
    assert date(2026, 7, 10) not in emp1_days
    # Tagdienst am 11.07. (Beginn 08:00) hätte 0h Ruhe nach externer Nacht.
    emp1_day_shifts = {(d, t) for d, t, e in result.assignments if e == 1}
    assert (date(2026, 7, 11), 1) not in emp1_day_shifts


def test_monthly_hours_capped():
    slots = make_slots(JULY_2026)
    employees = [make_employee(i, hours=30.0) for i in range(1, 9)]
    result = solve_schedule(JULY_2026, slots, employees, time_limit_seconds=20)
    assert result.feasible
    for e in employees:
        minutes = sum(TWELVE_H for _, _, emp in result.assignments
                      if emp == e.employee_id)
        assert minutes <= e.monthly_target_minutes + rules.MAX_MONTHLY_OVERTIME_MINUTES
