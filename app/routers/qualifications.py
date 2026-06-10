from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.auth import flash, get_current_user
from app.database import get_db
from app.templating import templates

router = APIRouter(prefix="/qualifikationen")


@router.get("")
def list_qualifications(request: Request, db: Session = Depends(get_db),
                        user: models.User = Depends(get_current_user)):
    qualifications = list(db.scalars(
        select(models.Qualification).order_by(models.Qualification.code)
    ))
    return templates.TemplateResponse(request, "qualifications.html", {
        "user": user, "qualifications": qualifications,
    })


@router.post("")
def create_qualification(request: Request, code: str = Form(...), name: str = Form(...),
                         db: Session = Depends(get_db),
                         user: models.User = Depends(get_current_user)):
    code = code.strip().upper()
    existing = db.scalar(select(models.Qualification)
                         .where(models.Qualification.code == code))
    if existing:
        flash(request, f"Kürzel „{code}“ existiert bereits.", "error")
    else:
        db.add(models.Qualification(code=code, name=name.strip()))
        db.commit()
        flash(request, f"Qualifikation „{code}“ angelegt.")
    return RedirectResponse("/qualifikationen", status_code=303)


@router.post("/{qualification_id}/loeschen")
def delete_qualification(qualification_id: int, request: Request,
                         db: Session = Depends(get_db),
                         user: models.User = Depends(get_current_user)):
    qualification = db.get(models.Qualification, qualification_id)
    if qualification:
        db.delete(qualification)
        db.commit()
        flash(request, f"Qualifikation „{qualification.code}“ gelöscht.", "warning")
    return RedirectResponse("/qualifikationen", status_code=303)
