"""Datenmodell der Mitarbeiter- und Dienstplanverwaltung.

Domäne: außerklinische Intensivpflege. Ein "Standort" ist eine Versorgung
(Wohngemeinschaft oder 1:1-Versorgung beim Klienten), die rund um die Uhr
mit qualifiziertem Personal besetzt werden muss.
"""
import enum
from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    PLANER = "PLANER"


class EmploymentType(str, enum.Enum):
    VOLLZEIT = "VOLLZEIT"
    TEILZEIT = "TEILZEIT"
    MINIJOB = "MINIJOB"


class ShiftCategory(str, enum.Enum):
    TAG = "TAG"
    NACHT = "NACHT"


class Preference(str, enum.Enum):
    BEVORZUGT = "BEVORZUGT"
    NEUTRAL = "NEUTRAL"
    AUSGESCHLOSSEN = "AUSGESCHLOSSEN"


class AbsenceType(str, enum.Enum):
    URLAUB = "URLAUB"
    KRANKHEIT = "KRANKHEIT"
    FORTBILDUNG = "FORTBILDUNG"
    SONSTIGES = "SONSTIGES"


class PlanStatus(str, enum.Enum):
    ENTWURF = "ENTWURF"
    VEROEFFENTLICHT = "VEROEFFENTLICHT"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.PLANER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


employee_qualifications = Table(
    "employee_qualifications",
    Base.metadata,
    Column("employee_id", ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True),
    Column("qualification_id", ForeignKey("qualifications.id", ondelete="CASCADE"), primary_key=True),
)

employee_locations = Table(
    "employee_locations",
    Base.metadata,
    Column("employee_id", ForeignKey("employees.id", ondelete="CASCADE"), primary_key=True),
    Column("location_id", ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True),
)


class Qualification(Base):
    __tablename__ = "qualifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(255))

    employees: Mapped[list["Employee"]] = relationship(
        secondary=employee_qualifications, back_populates="qualifications"
    )


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType), default=EmploymentType.VOLLZEIT
    )
    # Vertraglich vereinbarte Wochenarbeitszeit in Stunden.
    weekly_hours: Mapped[float] = mapped_column(Float, default=40.0)
    pref_day: Mapped[Preference] = mapped_column(Enum(Preference), default=Preference.NEUTRAL)
    pref_night: Mapped[Preference] = mapped_column(Enum(Preference), default=Preference.NEUTRAL)
    # Wochentage (0=Mo … 6=So), an denen grundsätzlich nicht gearbeitet wird,
    # als kommaseparierte Liste, z. B. "1,3".
    blocked_weekdays: Mapped[str] = mapped_column(String(20), default="")
    max_consecutive_days: Mapped[int] = mapped_column(Integer, default=6)
    max_consecutive_nights: Mapped[int] = mapped_column(Integer, default=4)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    qualifications: Mapped[list[Qualification]] = relationship(
        secondary=employee_qualifications, back_populates="employees"
    )
    locations: Mapped[list["Location"]] = relationship(
        secondary=employee_locations, back_populates="employees"
    )
    absences: Mapped[list["Absence"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def blocked_weekday_set(self) -> set[int]:
        return {int(x) for x in self.blocked_weekdays.split(",") if x.strip() != ""}

    def monthly_target_minutes(self, year: int, month: int) -> int:
        import calendar

        days = calendar.monthrange(year, month)[1]
        return round(self.weekly_hours * days / 7 * 60)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    employees: Mapped[list[Employee]] = relationship(
        secondary=employee_locations, back_populates="locations"
    )
    shift_templates: Mapped[list["ShiftTemplate"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )
    plans: Mapped[list["SchedulePlan"]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )


class ShiftTemplate(Base):
    """Dienstart eines Standorts, z. B. Tagdienst 08:00–20:00, Besetzung 1."""

    __tablename__ = "shift_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[ShiftCategory] = mapped_column(Enum(ShiftCategory))
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    staff_needed: Mapped[int] = mapped_column(Integer, default=1)
    required_qualification_id: Mapped[int | None] = mapped_column(
        ForeignKey("qualifications.id", ondelete="SET NULL"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    location: Mapped[Location] = relationship(back_populates="shift_templates")
    required_qualification: Mapped[Qualification | None] = relationship()

    @property
    def duration_minutes(self) -> int:
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        if end <= start:  # Dienst geht über Mitternacht
            end += 24 * 60
        return end - start

    @property
    def crosses_midnight(self) -> bool:
        return (self.end_time.hour, self.end_time.minute) <= (
            self.start_time.hour,
            self.start_time.minute,
        )

    def interval(self, day: date) -> tuple[datetime, datetime]:
        from datetime import timedelta

        start = datetime.combine(day, self.start_time)
        end = datetime.combine(day, self.end_time)
        if end <= start:
            end += timedelta(days=1)
        return start, end


class Absence(Base):
    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    type: Mapped[AbsenceType] = mapped_column(Enum(AbsenceType), default=AbsenceType.URLAUB)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    note: Mapped[str] = mapped_column(String(255), default="")

    employee: Mapped[Employee] = relationship(back_populates="absences")


class SchedulePlan(Base):
    """Dienstplan eines Standorts für einen Kalendermonat."""

    __tablename__ = "schedule_plans"
    __table_args__ = (UniqueConstraint("location_id", "year", "month", name="uq_plan_loc_month"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    status: Mapped[PlanStatus] = mapped_column(Enum(PlanStatus), default=PlanStatus.ENTWURF)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    location: Mapped[Location] = relationship(back_populates="plans")
    assignments: Mapped[list["ShiftAssignment"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )


class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    __table_args__ = (
        UniqueConstraint(
            "plan_id", "date", "shift_template_id", "employee_id", name="uq_assignment"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("schedule_plans.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date, index=True)
    shift_template_id: Mapped[int] = mapped_column(
        ForeignKey("shift_templates.id", ondelete="CASCADE")
    )
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id", ondelete="CASCADE"))
    # Manuell gesetzte Zuweisungen bleiben bei automatischer Neuplanung erhalten.
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)

    plan: Mapped[SchedulePlan] = relationship(back_populates="assignments")
    shift_template: Mapped[ShiftTemplate] = relationship()
    employee: Mapped[Employee] = relationship()
