from datetime import time

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.auth import flash, get_current_user
from app.database import get_db
from app.scheduling.rules import MAX_SHIFT_HOURS
from app.templating import templates

router = APIRouter(prefix="/standorte")


@router.get("")
def list_locations(request: Request, db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    locations = list(db.scalars(select(models.Location).order_by(models.Location.name)))
    return templates.TemplateResponse(request, "locations/list.html", {
        "user": user, "locations": locations,
    })


@router.get("/neu")
def new_location_form(request: Request, db: Session = Depends(get_db),
                      user: models.User = Depends(get_current_user)):
    return templates.TemplateResponse(request, "locations/form.html", {
        "user": user, "location": None,
    })


@router.post("/neu")
def create_location(request: Request, name: str = Form(...), address: str = Form(""),
                    city: str = Form(""), notes: str = Form(""),
                    db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    location = models.Location(name=name.strip(), address=address.strip(),
                               city=city.strip(), notes=notes.strip())
    db.add(location)
    db.commit()
    # Standard-Dienste für 24h-Versorgung anlegen.
    db.add_all([
        models.ShiftTemplate(location_id=location.id, name="Tagdienst",
                             category=models.ShiftCategory.TAG,
                             start_time=time(8, 0), end_time=time(20, 0), staff_needed=1),
        models.ShiftTemplate(location_id=location.id, name="Nachtdienst",
                             category=models.ShiftCategory.NACHT,
                             start_time=time(20, 0), end_time=time(8, 0), staff_needed=1),
    ])
    db.commit()
    flash(request, f"Standort „{location.name}“ mit Standard-Diensten (Tag/Nacht) angelegt.")
    return RedirectResponse(f"/standorte/{location.id}", status_code=303)


@router.get("/{location_id}")
def location_detail(location_id: int, request: Request, db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    if not location:
        raise HTTPException(404)
    assigned_ids = {e.id for e in location.employees}
    available = [
        e for e in db.scalars(select(models.Employee)
                              .where(models.Employee.active)
                              .order_by(models.Employee.last_name))
        if e.id not in assigned_ids
    ]
    qualifications = list(db.scalars(select(models.Qualification)
                                     .order_by(models.Qualification.code)))
    plans = sorted(location.plans, key=lambda p: (p.year, p.month), reverse=True)
    return templates.TemplateResponse(request, "locations/detail.html", {
        "user": user,
        "location": location,
        "available_employees": available,
        "qualifications": qualifications,
        "plans": plans,
        "categories": list(models.ShiftCategory),
    })


@router.post("/{location_id}/bearbeiten")
def update_location(location_id: int, request: Request, name: str = Form(...),
                    address: str = Form(""), city: str = Form(""), notes: str = Form(""),
                    active: str = Form(None), db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    if not location:
        raise HTTPException(404)
    location.name = name.strip()
    location.address = address.strip()
    location.city = city.strip()
    location.notes = notes.strip()
    location.active = active == "on"
    db.commit()
    flash(request, "Standort gespeichert.")
    return RedirectResponse(f"/standorte/{location_id}", status_code=303)


@router.post("/{location_id}/loeschen")
def delete_location(location_id: int, request: Request, db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    if location:
        db.delete(location)
        db.commit()
        flash(request, f"Standort „{location.name}“ gelöscht.", "warning")
    return RedirectResponse("/standorte", status_code=303)


@router.post("/{location_id}/mitarbeiter")
def assign_employee(location_id: int, request: Request, employee_id: int = Form(...),
                    db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    employee = db.get(models.Employee, employee_id)
    if not location or not employee:
        raise HTTPException(404)
    if employee not in location.employees:
        location.employees.append(employee)
        db.commit()
        flash(request, f"{employee.full_name} dem Standort zugewiesen.")
    return RedirectResponse(f"/standorte/{location_id}", status_code=303)


@router.post("/{location_id}/mitarbeiter/{employee_id}/entfernen")
def unassign_employee(location_id: int, employee_id: int, request: Request,
                      db: Session = Depends(get_db),
                      user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    employee = db.get(models.Employee, employee_id)
    if location and employee and employee in location.employees:
        location.employees.remove(employee)
        db.commit()
        flash(request, f"{employee.full_name} vom Standort entfernt.", "warning")
    return RedirectResponse(f"/standorte/{location_id}", status_code=303)


@router.post("/{location_id}/dienste")
def add_shift_template(location_id: int, request: Request, name: str = Form(...),
                       category: str = Form(...), start_time_str: str = Form(...),
                       end_time_str: str = Form(...), staff_needed: int = Form(1),
                       required_qualification_id: str = Form(""),
                       db: Session = Depends(get_db),
                       user: models.User = Depends(get_current_user)):
    location = db.get(models.Location, location_id)
    if not location:
        raise HTTPException(404)
    start = time.fromisoformat(start_time_str)
    end = time.fromisoformat(end_time_str)
    template = models.ShiftTemplate(
        location_id=location_id,
        name=name.strip(),
        category=models.ShiftCategory(category),
        start_time=start,
        end_time=end,
        staff_needed=max(1, staff_needed),
        required_qualification_id=int(required_qualification_id)
        if required_qualification_id else None,
    )
    if template.duration_minutes > MAX_SHIFT_HOURS * 60:
        flash(request, f"Dienst nicht angelegt: länger als {MAX_SHIFT_HOURS} Stunden "
                       f"(§3/§7 ArbZG).", "error")
        return RedirectResponse(f"/standorte/{location_id}", status_code=303)
    db.add(template)
    db.commit()
    flash(request, f"Dienst „{template.name}“ angelegt.")
    return RedirectResponse(f"/standorte/{location_id}", status_code=303)


@router.post("/{location_id}/dienste/{template_id}/loeschen")
def delete_shift_template(location_id: int, template_id: int, request: Request,
                          db: Session = Depends(get_db),
                          user: models.User = Depends(get_current_user)):
    template = db.get(models.ShiftTemplate, template_id)
    if template and template.location_id == location_id:
        db.delete(template)
        db.commit()
        flash(request, "Dienst gelöscht (inkl. zugehöriger Planeinträge).", "warning")
    return RedirectResponse(f"/standorte/{location_id}", status_code=303)
