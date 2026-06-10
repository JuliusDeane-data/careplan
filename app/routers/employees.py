from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.auth import flash, get_current_user
from app.database import get_db
from app.templating import templates

router = APIRouter(prefix="/mitarbeiter")

WEEKDAY_LABELS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def _form_context(db: Session, employee: models.Employee | None) -> dict:
    return {
        "employee": employee,
        "qualifications": list(db.scalars(select(models.Qualification)
                                          .order_by(models.Qualification.code))),
        "locations": list(db.scalars(select(models.Location)
                                     .where(models.Location.active)
                                     .order_by(models.Location.name))),
        "weekday_labels": WEEKDAY_LABELS,
        "employment_types": list(models.EmploymentType),
        "preferences": list(models.Preference),
    }


@router.get("")
def list_employees(request: Request, q: str = "", db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    stmt = select(models.Employee).order_by(models.Employee.last_name,
                                            models.Employee.first_name)
    employees = list(db.scalars(stmt))
    if q:
        needle = q.lower()
        employees = [e for e in employees if needle in e.full_name.lower()]
    return templates.TemplateResponse(request, "employees/list.html", {
        "user": user, "employees": employees, "q": q,
    })


@router.get("/neu")
def new_employee_form(request: Request, db: Session = Depends(get_db),
                      user: models.User = Depends(get_current_user)):
    ctx = _form_context(db, None)
    ctx["user"] = user
    return templates.TemplateResponse(request, "employees/form.html", ctx)


async def _apply_form(request: Request, db: Session, employee: models.Employee):
    form = await request.form()
    employee.first_name = form.get("first_name", "").strip()
    employee.last_name = form.get("last_name", "").strip()
    employee.email = form.get("email", "").strip() or None
    employee.phone = form.get("phone", "").strip() or None
    employee.employment_type = models.EmploymentType(form.get("employment_type", "VOLLZEIT"))
    employee.weekly_hours = float(form.get("weekly_hours", "40").replace(",", "."))
    employee.pref_day = models.Preference(form.get("pref_day", "NEUTRAL"))
    employee.pref_night = models.Preference(form.get("pref_night", "NEUTRAL"))
    employee.max_consecutive_days = max(1, min(6, int(form.get("max_consecutive_days", 6))))
    employee.max_consecutive_nights = max(1, min(5, int(form.get("max_consecutive_nights", 4))))
    employee.blocked_weekdays = ",".join(sorted(form.getlist("blocked_weekdays")))
    employee.active = form.get("active") == "on"
    employee.notes = form.get("notes", "").strip()

    qual_ids = [int(x) for x in form.getlist("qualifications")]
    employee.qualifications = list(db.scalars(
        select(models.Qualification).where(models.Qualification.id.in_(qual_ids))
    )) if qual_ids else []
    loc_ids = [int(x) for x in form.getlist("locations")]
    employee.locations = list(db.scalars(
        select(models.Location).where(models.Location.id.in_(loc_ids))
    )) if loc_ids else []

    if not employee.first_name or not employee.last_name:
        raise ValueError("Vor- und Nachname sind Pflichtfelder.")
    if employee.pref_day == models.Preference.AUSGESCHLOSSEN \
            and employee.pref_night == models.Preference.AUSGESCHLOSSEN:
        raise ValueError("Tag- und Nachtdienst dürfen nicht beide ausgeschlossen sein.")


@router.post("/neu")
async def create_employee(request: Request, db: Session = Depends(get_db),
                          user: models.User = Depends(get_current_user)):
    employee = models.Employee(first_name="", last_name="")
    try:
        await _apply_form(request, db, employee)
    except ValueError as exc:
        ctx = _form_context(db, employee)
        ctx.update({"user": user, "error": str(exc)})
        return templates.TemplateResponse(request, "employees/form.html", ctx, status_code=400)
    db.add(employee)
    db.commit()
    flash(request, f"Mitarbeiter:in {employee.full_name} angelegt.")
    return RedirectResponse(f"/mitarbeiter/{employee.id}", status_code=303)


@router.get("/{employee_id}")
def employee_detail(employee_id: int, request: Request, db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    employee = db.get(models.Employee, employee_id)
    if not employee:
        raise HTTPException(404)
    absences = sorted(employee.absences, key=lambda a: a.start_date, reverse=True)
    return templates.TemplateResponse(request, "employees/detail.html", {
        "user": user,
        "employee": employee,
        "absences": absences,
        "absence_types": list(models.AbsenceType),
        "weekday_labels": WEEKDAY_LABELS,
        "today": date.today(),
    })


@router.get("/{employee_id}/bearbeiten")
def edit_employee_form(employee_id: int, request: Request, db: Session = Depends(get_db),
                       user: models.User = Depends(get_current_user)):
    employee = db.get(models.Employee, employee_id)
    if not employee:
        raise HTTPException(404)
    ctx = _form_context(db, employee)
    ctx["user"] = user
    return templates.TemplateResponse(request, "employees/form.html", ctx)


@router.post("/{employee_id}/bearbeiten")
async def update_employee(employee_id: int, request: Request, db: Session = Depends(get_db),
                          user: models.User = Depends(get_current_user)):
    employee = db.get(models.Employee, employee_id)
    if not employee:
        raise HTTPException(404)
    try:
        await _apply_form(request, db, employee)
    except ValueError as exc:
        ctx = _form_context(db, employee)
        ctx.update({"user": user, "error": str(exc)})
        return templates.TemplateResponse(request, "employees/form.html", ctx, status_code=400)
    db.commit()
    flash(request, "Änderungen gespeichert.")
    return RedirectResponse(f"/mitarbeiter/{employee.id}", status_code=303)


@router.post("/{employee_id}/loeschen")
def delete_employee(employee_id: int, request: Request, db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    employee = db.get(models.Employee, employee_id)
    if employee:
        db.delete(employee)
        db.commit()
        flash(request, f"Mitarbeiter:in {employee.full_name} gelöscht.", "warning")
    return RedirectResponse("/mitarbeiter", status_code=303)


@router.post("/{employee_id}/abwesenheiten")
def add_absence(employee_id: int, request: Request,
                type: str = Form(...), start_date: date = Form(...),
                end_date: date = Form(...), note: str = Form(""),
                db: Session = Depends(get_db),
                user: models.User = Depends(get_current_user)):
    employee = db.get(models.Employee, employee_id)
    if not employee:
        raise HTTPException(404)
    if end_date < start_date:
        flash(request, "Das Enddatum liegt vor dem Startdatum.", "error")
    else:
        db.add(models.Absence(
            employee_id=employee_id,
            type=models.AbsenceType(type),
            start_date=start_date,
            end_date=end_date,
            note=note.strip(),
        ))
        db.commit()
        flash(request, "Abwesenheit eingetragen.")
    return RedirectResponse(f"/mitarbeiter/{employee_id}", status_code=303)


@router.post("/{employee_id}/abwesenheiten/{absence_id}/loeschen")
def delete_absence(employee_id: int, absence_id: int, request: Request,
                   db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    absence = db.get(models.Absence, absence_id)
    if absence and absence.employee_id == employee_id:
        db.delete(absence)
        db.commit()
        flash(request, "Abwesenheit gelöscht.", "warning")
    return RedirectResponse(f"/mitarbeiter/{employee_id}", status_code=303)
