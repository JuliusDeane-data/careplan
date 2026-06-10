from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.auth import flash, get_current_user
from app.database import get_db
from app.scheduling import service
from app.templating import templates

router = APIRouter(prefix="/dienstplaene")


@router.get("")
def list_plans(request: Request, db: Session = Depends(get_db),
               user: models.User = Depends(get_current_user)):
    plans = list(db.scalars(
        select(models.SchedulePlan)
        .order_by(models.SchedulePlan.year.desc(), models.SchedulePlan.month.desc())
    ))
    locations = list(db.scalars(
        select(models.Location).where(models.Location.active)
        .order_by(models.Location.name)
    ))
    today = date.today()
    default_month = f"{today.year + (1 if today.month == 12 else 0)}-" \
                    f"{(today.month % 12) + 1:02d}"
    return templates.TemplateResponse(request, "plans/list.html", {
        "user": user, "plans": plans, "locations": locations,
        "default_month": default_month,
    })


@router.post("")
def create_plan(request: Request, location_id: int = Form(...), month: str = Form(...),
                db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    if not location:
        raise HTTPException(404)
    try:
        year_str, month_str = month.split("-")
        year, mon = int(year_str), int(month_str)
        assert 1 <= mon <= 12 and 2000 <= year <= 2100
    except (ValueError, AssertionError):
        flash(request, "Ungültiger Monat.", "error")
        return RedirectResponse("/dienstplaene", status_code=303)

    existing = db.scalar(select(models.SchedulePlan).where(
        models.SchedulePlan.location_id == location_id,
        models.SchedulePlan.year == year,
        models.SchedulePlan.month == mon,
    ))
    if existing:
        flash(request, "Für diesen Standort und Monat existiert bereits ein Plan.", "error")
        return RedirectResponse(f"/dienstplaene/{existing.id}", status_code=303)

    plan = models.SchedulePlan(location_id=location_id, year=year, month=mon)
    db.add(plan)
    db.commit()
    flash(request, f"Dienstplan für {location.name} angelegt.")
    return RedirectResponse(f"/dienstplaene/{plan.id}", status_code=303)


def _grid_context(db: Session, plan: models.SchedulePlan) -> dict:
    days = service.month_days(plan.year, plan.month)
    templates_active = [t for t in plan.location.shift_templates if t.active]

    cells: dict[tuple[date, int], list[models.ShiftAssignment]] = {}
    for a in plan.assignments:
        cells.setdefault((a.date, a.shift_template_id), []).append(a)
    for key in cells:
        cells[key].sort(key=lambda a: a.employee.last_name)

    location_employees = sorted(
        [e for e in plan.location.employees if e.active],
        key=lambda e: (e.last_name, e.first_name),
    )

    # Abwesenheits-Lookup pro Tag für die Auswahlfelder.
    absent: dict[date, set[int]] = {d: set() for d in days}
    for e in location_employees:
        for a in e.absences:
            for d in days:
                if a.start_date <= d <= a.end_date:
                    absent[d].add(e.id)

    violations = service.validate_plan(db, plan)
    violation_days: dict[date, list] = {}
    violation_cells: set[tuple[date, int]] = set()
    for v in violations:
        violation_days.setdefault(v.day, []).append(v)
        if v.severity == "ERROR":
            violation_cells.add((v.day, v.employee_id))

    summary = service.plan_summary(db, plan)
    return {
        "plan": plan,
        "days": days,
        "shift_templates": templates_active,
        "cells": cells,
        "location_employees": location_employees,
        "absent": absent,
        "violations": violations,
        "violation_cells": violation_cells,
        "summary": summary,
        "error_count": sum(1 for v in violations if v.severity == "ERROR"),
        "warn_count": sum(1 for v in violations if v.severity == "WARN"),
    }


@router.get("/{plan_id}")
def plan_detail(plan_id: int, request: Request, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    plan = db.get(models.SchedulePlan, plan_id)
    if not plan:
        raise HTTPException(404)
    ctx = _grid_context(db, plan)
    ctx["user"] = user
    return templates.TemplateResponse(request, "plans/detail.html", ctx)


@router.post("/{plan_id}/generieren")
def generate(plan_id: int, request: Request, db: Session = Depends(get_db),
             user: models.User = Depends(get_current_user)):
    plan = db.get(models.SchedulePlan, plan_id)
    if not plan:
        raise HTTPException(404)
    if not [t for t in plan.location.shift_templates if t.active]:
        flash(request, "Der Standort hat keine aktiven Dienste.", "error")
        return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)
    if not [e for e in plan.location.employees if e.active]:
        flash(request, "Dem Standort sind keine aktiven Mitarbeiter zugewiesen.", "error")
        return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)

    result = service.generate_plan(db, plan)
    if not result.feasible:
        flash(request, "Keine zulässige Lösung gefunden – gepinnte Zuweisungen oder "
                       "Regeln verhindern einen gültigen Plan.", "error")
    else:
        unfilled_count = sum(n for _, _, n in result.unfilled)
        msg = (f"Plan erstellt ({result.status}, "
               f"{result.stats.get('wall_time', '?')}s).")
        if unfilled_count:
            flash(request, msg + f" {unfilled_count} Dienste konnten nicht besetzt "
                                 f"werden – mehr Personal zuweisen.", "warning")
        else:
            flash(request, msg + " Alle Dienste besetzt.")
    return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)


@router.post("/{plan_id}/zuweisung")
def set_assignment(plan_id: int, request: Request,
                   day: date = Form(...), template_id: int = Form(...),
                   employee_id: str = Form(""), assignment_id: str = Form(""),
                   db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    """Manuelles Setzen/Ändern/Entfernen einer Zuweisung (wird gepinnt)."""
    plan = db.get(models.SchedulePlan, plan_id)
    if not plan:
        raise HTTPException(404)

    existing = db.get(models.ShiftAssignment, int(assignment_id)) if assignment_id else None
    if existing and existing.plan_id != plan_id:
        raise HTTPException(400)

    new_emp_id = int(employee_id) if employee_id else None

    if existing and new_emp_id is None:
        db.delete(existing)
        flash(request, "Zuweisung entfernt.", "warning")
    elif existing and new_emp_id:
        duplicate = db.scalar(select(models.ShiftAssignment).where(
            models.ShiftAssignment.plan_id == plan_id,
            models.ShiftAssignment.date == day,
            models.ShiftAssignment.shift_template_id == template_id,
            models.ShiftAssignment.employee_id == new_emp_id,
            models.ShiftAssignment.id != existing.id,
        ))
        if duplicate:
            flash(request, "Diese Person ist in diesem Dienst bereits eingeteilt.", "error")
            return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)
        existing.employee_id = new_emp_id
        existing.pinned = True
        flash(request, "Zuweisung geändert und fixiert.")
    elif not existing and new_emp_id:
        duplicate = db.scalar(select(models.ShiftAssignment).where(
            models.ShiftAssignment.plan_id == plan_id,
            models.ShiftAssignment.date == day,
            models.ShiftAssignment.shift_template_id == template_id,
            models.ShiftAssignment.employee_id == new_emp_id,
        ))
        if duplicate:
            flash(request, "Diese Person ist in diesem Dienst bereits eingeteilt.", "error")
            return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)
        db.add(models.ShiftAssignment(
            plan_id=plan_id, date=day, shift_template_id=template_id,
            employee_id=new_emp_id, pinned=True,
        ))
        flash(request, "Zuweisung gesetzt und fixiert.")
    db.commit()
    return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)


@router.post("/{plan_id}/pin")
def toggle_pin(plan_id: int, request: Request, assignment_id: int = Form(...),
               db: Session = Depends(get_db),
               user: models.User = Depends(get_current_user)):
    assignment = db.get(models.ShiftAssignment, assignment_id)
    if assignment and assignment.plan_id == plan_id:
        assignment.pinned = not assignment.pinned
        db.commit()
    return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)


@router.post("/{plan_id}/status")
def toggle_status(plan_id: int, request: Request, db: Session = Depends(get_db),
                  user: models.User = Depends(get_current_user)):
    plan = db.get(models.SchedulePlan, plan_id)
    if not plan:
        raise HTTPException(404)
    if plan.status == models.PlanStatus.ENTWURF:
        plan.status = models.PlanStatus.VEROEFFENTLICHT
        flash(request, "Plan veröffentlicht.")
    else:
        plan.status = models.PlanStatus.ENTWURF
        flash(request, "Plan zurück in den Entwurfsmodus gesetzt.", "warning")
    db.commit()
    return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)


@router.post("/{plan_id}/leeren")
def clear_plan(plan_id: int, request: Request, db: Session = Depends(get_db),
               user: models.User = Depends(get_current_user)):
    plan = db.get(models.SchedulePlan, plan_id)
    if not plan:
        raise HTTPException(404)
    for a in list(plan.assignments):
        db.delete(a)
    db.commit()
    flash(request, "Alle Zuweisungen entfernt.", "warning")
    return RedirectResponse(f"/dienstplaene/{plan_id}", status_code=303)


@router.post("/{plan_id}/loeschen")
def delete_plan(plan_id: int, request: Request, db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    plan = db.get(models.SchedulePlan, plan_id)
    if plan:
        db.delete(plan)
        db.commit()
        flash(request, "Dienstplan gelöscht.", "warning")
    return RedirectResponse("/dienstplaene", status_code=303)
