"""Verbindet Datenbank, Solver und Regel-Validierung."""
import calendar
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models
from app.scheduling import rules
from app.scheduling.solver import EmployeeSpec, SlotSpec, SolveResult, solve_schedule


def month_days(year: int, month: int) -> list[date]:
    last = calendar.monthrange(year, month)[1]
    return [date(year, month, d) for d in range(1, last + 1)]


def _time_to_minutes(t) -> int:
    return t.hour * 60 + t.minute


def _other_assignments(db: Session, employee_ids: list[int], plan: models.SchedulePlan,
                       window_start: date, window_end: date) -> list[models.ShiftAssignment]:
    """Zuweisungen der Mitarbeiter außerhalb des gegebenen Plans im Zeitfenster
    (andere Standorte und angrenzende Monate)."""
    if not employee_ids:
        return []
    stmt = (
        select(models.ShiftAssignment)
        .options(
            joinedload(models.ShiftAssignment.shift_template)
            .joinedload(models.ShiftTemplate.location),
        )
        .where(
            models.ShiftAssignment.employee_id.in_(employee_ids),
            models.ShiftAssignment.plan_id != plan.id,
            models.ShiftAssignment.date >= window_start,
            models.ShiftAssignment.date <= window_end,
        )
    )
    return list(db.scalars(stmt).unique())


def generate_plan(db: Session, plan: models.SchedulePlan,
                  time_limit_seconds: float = 15.0) -> SolveResult:
    """Erzeugt den Dienstplan automatisch. Gepinnte (manuell gesetzte)
    Zuweisungen bleiben erhalten, alle übrigen werden neu geplant."""
    location = plan.location
    days = month_days(plan.year, plan.month)
    window_start = days[0] - timedelta(days=7)
    window_end = days[-1] + timedelta(days=7)

    templates = [t for t in location.shift_templates if t.active]
    slots = [
        SlotSpec(
            day=d,
            template_id=t.id,
            start_minutes=_time_to_minutes(t.start_time),
            duration_minutes=t.duration_minutes,
            is_night=t.category == models.ShiftCategory.NACHT,
            staff_needed=t.staff_needed,
            required_qualification_id=t.required_qualification_id,
        )
        for d in days
        for t in templates
    ]

    employees = [e for e in location.employees if e.active]
    emp_ids = [e.id for e in employees]
    external = _other_assignments(db, emp_ids, plan, window_start, window_end)
    ext_by_emp: dict[int, list[models.ShiftAssignment]] = {}
    for a in external:
        ext_by_emp.setdefault(a.employee_id, []).append(a)

    specs = []
    for e in employees:
        ext_shifts = []
        ext_month_minutes = 0
        for a in ext_by_emp.get(e.id, []):
            t = a.shift_template
            ext_shifts.append((
                a.date,
                _time_to_minutes(t.start_time),
                t.duration_minutes,
                t.category == models.ShiftCategory.NACHT,
            ))
            if a.date.year == plan.year and a.date.month == plan.month:
                ext_month_minutes += t.duration_minutes
        specs.append(EmployeeSpec(
            employee_id=e.id,
            name=e.full_name,
            qualification_ids={q.id for q in e.qualifications},
            monthly_target_minutes=e.monthly_target_minutes(plan.year, plan.month),
            pref_day=e.pref_day.value,
            pref_night=e.pref_night.value,
            blocked_weekdays=e.blocked_weekday_set,
            max_consecutive_days=e.max_consecutive_days,
            max_consecutive_nights=e.max_consecutive_nights,
            absences=[(a.start_date, a.end_date) for a in e.absences],
            external_shifts=ext_shifts,
            external_month_minutes=ext_month_minutes,
        ))

    pinned = [
        (a.date, a.shift_template_id, a.employee_id)
        for a in plan.assignments
        if a.pinned
    ]

    result = solve_schedule(days, slots, specs, pinned=pinned,
                            time_limit_seconds=time_limit_seconds)
    if not result.feasible:
        return result

    # Nicht gepinnte Zuweisungen ersetzen.
    pinned_keys = set(pinned)
    for a in list(plan.assignments):
        if not a.pinned:
            db.delete(a)
    db.flush()
    for day, template_id, employee_id in result.assignments:
        if (day, template_id, employee_id) in pinned_keys:
            continue
        db.add(models.ShiftAssignment(
            plan_id=plan.id,
            date=day,
            shift_template_id=template_id,
            employee_id=employee_id,
            pinned=False,
        ))
    db.commit()
    return result


def validate_plan(db: Session, plan: models.SchedulePlan) -> list[rules.Violation]:
    """Prüft alle Zuweisungen des Plans (inkl. Dienste derselben Mitarbeiter
    an anderen Standorten und in Nachbarmonaten) gegen das Regelwerk."""
    days = month_days(plan.year, plan.month)
    window_start = days[0] - timedelta(days=7)
    window_end = days[-1] + timedelta(days=7)

    emp_ids = sorted({a.employee_id for a in plan.assignments})
    if not emp_ids:
        return []
    external = _other_assignments(db, emp_ids, plan, window_start, window_end)

    employees = {
        e.id: e
        for e in db.scalars(select(models.Employee).where(models.Employee.id.in_(emp_ids)))
    }

    violations: list[rules.Violation] = []
    for emp_id in emp_ids:
        e = employees[emp_id]
        shifts = []
        for a in list(plan.assignments) + external:
            if a.employee_id != emp_id:
                continue
            t = a.shift_template
            shifts.append(rules.make_shift_info(
                a.date, t.start_time, t.end_time,
                is_night=t.category == models.ShiftCategory.NACHT,
                location_name=t.location.name,
                shift_name=t.name,
            ))
        emp_rules = rules.EmployeeRules(
            employee_id=e.id,
            name=e.full_name,
            max_consecutive_days=e.max_consecutive_days,
            max_consecutive_nights=e.max_consecutive_nights,
            blocked_weekdays=e.blocked_weekday_set,
            night_excluded=e.pref_night == models.Preference.AUSGESCHLOSSEN,
            day_excluded=e.pref_day == models.Preference.AUSGESCHLOSSEN,
            absences=[(a.start_date, a.end_date) for a in e.absences],
            monthly_target_minutes=e.monthly_target_minutes(plan.year, plan.month),
        )
        violations.extend(
            rules.find_violations(emp_rules, shifts, month=(plan.year, plan.month))
        )
    # Nur Verstöße anzeigen, die den Planmonat betreffen.
    return [v for v in violations
            if days[0] <= v.day <= days[-1] or v.code in ("MONATSSTUNDEN", "FREIES_WOCHENENDE")]


def plan_summary(db: Session, plan: models.SchedulePlan) -> dict:
    """Kennzahlen für die Plan-Ansicht: Stunden je Mitarbeiter, Besetzungsgrad."""
    days = month_days(plan.year, plan.month)
    templates = [t for t in plan.location.shift_templates if t.active]
    needed_total = sum(t.staff_needed for t in templates) * len(days)

    def empty_entry(e: models.Employee) -> dict:
        return {
            "employee": e,
            "minutes": 0,
            "shifts": 0,
            "nights": 0,
            "weekend_shifts": 0,
            "target_minutes": e.monthly_target_minutes(plan.year, plan.month),
        }

    # Alle aktiven Teammitglieder anzeigen – auch ohne Dienste in diesem Plan,
    # damit sichtbar ist, wer z. B. an anderen Standorten verplant ist.
    per_employee: dict[int, dict] = {
        e.id: empty_entry(e) for e in plan.location.employees if e.active
    }
    for a in plan.assignments:
        t = a.shift_template
        e = a.employee
        entry = per_employee.setdefault(e.id, empty_entry(e))
        entry["minutes"] += t.duration_minutes
        entry["shifts"] += 1
        if t.category == models.ShiftCategory.NACHT:
            entry["nights"] += 1
        if a.date.weekday() >= 5:
            entry["weekend_shifts"] += 1

    # Minuten an anderen Standorten im selben Monat ergänzen.
    emp_ids = list(per_employee.keys())
    if emp_ids:
        external = _other_assignments(db, emp_ids, plan, days[0], days[-1])
        for a in external:
            if a.employee_id in per_employee:
                per_employee[a.employee_id].setdefault("external_minutes", 0)
                per_employee[a.employee_id]["external_minutes"] += \
                    a.shift_template.duration_minutes
    for entry in per_employee.values():
        entry.setdefault("external_minutes", 0)
        entry["total_minutes"] = entry["minutes"] + entry["external_minutes"]
        entry["diff_minutes"] = entry["total_minutes"] - entry["target_minutes"]

    assigned_count = len(plan.assignments)
    return {
        "per_employee": sorted(per_employee.values(),
                               key=lambda x: x["employee"].last_name),
        "needed_total": needed_total,
        "assigned_total": assigned_count,
        "fill_rate": (assigned_count / needed_total * 100) if needed_total else 0,
    }
