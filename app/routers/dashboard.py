from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.database import get_db
from app.scheduling import service
from app.templating import templates

router = APIRouter()


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db),
              user: models.User = Depends(get_current_user)):
    today = date.today()
    employee_count = db.scalar(
        select(func.count()).select_from(models.Employee).where(models.Employee.active)
    )
    location_count = db.scalar(
        select(func.count()).select_from(models.Location).where(models.Location.active)
    )

    current_plans = list(db.scalars(
        select(models.SchedulePlan)
        .where(models.SchedulePlan.year == today.year,
               models.SchedulePlan.month == today.month)
    ))
    plan_cards = []
    for plan in current_plans:
        summary = service.plan_summary(db, plan)
        violations = service.validate_plan(db, plan)
        plan_cards.append({
            "plan": plan,
            "fill_rate": summary["fill_rate"],
            "errors": sum(1 for v in violations if v.severity == "ERROR"),
            "warnings": sum(1 for v in violations if v.severity == "WARN"),
        })

    upcoming_absences = list(db.scalars(
        select(models.Absence)
        .where(models.Absence.end_date >= today,
               models.Absence.start_date <= today + timedelta(days=30))
        .order_by(models.Absence.start_date)
        .limit(10)
    ))

    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "employee_count": employee_count,
        "location_count": location_count,
        "plan_cards": plan_cards,
        "upcoming_absences": upcoming_absences,
        "today": today,
    })
