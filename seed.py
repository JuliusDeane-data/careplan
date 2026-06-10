"""Legt Demo-Daten an: Qualifikationen, Standorte, Mitarbeiter, Abwesenheiten
und einen automatisch generierten Dienstplan für den Folgemonat.

Aufruf:  python seed.py
"""
from datetime import date, time, timedelta

from app.auth import ensure_default_admin
from app.database import SessionLocal, init_db
from app import models
from app.models import (
    AbsenceType, Employee, EmploymentType, Location, Preference, Qualification,
    SchedulePlan, ShiftCategory, ShiftTemplate,
)
from app.scheduling import service


def run():
    init_db()
    db = SessionLocal()
    try:
        ensure_default_admin(db)
        if db.query(Employee).count() > 0:
            print("Es existieren bereits Daten – Seed wird übersprungen.")
            return

        # Qualifikationen
        pfk = Qualification(code="PFK", name="Pflegefachkraft (examiniert)")
        beat = Qualification(code="BEAT", name="Basiskurs außerklinische Beatmung")
        fai = Qualification(code="FAI", name="Fachpflege Anästhesie/Intensiv")
        phk = Qualification(code="PHK", name="Pflegehilfskraft")
        db.add_all([pfk, beat, fai, phk])
        db.flush()

        # Standorte mit Diensten (24h-Versorgung, 12h-Dienste)
        def make_location(name, address, city, day_staff=1, night_staff=1,
                          required=None):
            loc = Location(name=name, address=address, city=city)
            db.add(loc)
            db.flush()
            db.add_all([
                ShiftTemplate(location_id=loc.id, name="Tagdienst",
                              category=ShiftCategory.TAG,
                              start_time=time(8, 0), end_time=time(20, 0),
                              staff_needed=day_staff,
                              required_qualification_id=required.id if required else None),
                ShiftTemplate(location_id=loc.id, name="Nachtdienst",
                              category=ShiftCategory.NACHT,
                              start_time=time(20, 0), end_time=time(8, 0),
                              staff_needed=night_staff,
                              required_qualification_id=required.id if required else None),
            ])
            return loc

        wg_sonnenhof = make_location("WG Sonnenhof", "Lindenstraße 12", "Köln",
                                     day_staff=2, night_staff=1, required=pfk)
        familie_krause = make_location("Familie Krause (1:1)", "Am Weiher 3", "Bergisch Gladbach",
                                       required=pfk)
        wg_hafenblick = make_location("WG Hafenblick", "Kaistraße 8", "Düsseldorf",
                                      required=pfk)
        db.flush()

        # Mitarbeiter
        def employee(first, last, hours, quals, locs, etype=EmploymentType.VOLLZEIT,
                     pref_day=Preference.NEUTRAL, pref_night=Preference.NEUTRAL,
                     blocked="", max_nights=4):
            e = Employee(
                first_name=first, last_name=last,
                email=f"{first.lower()}.{last.lower()}@careplan.local",
                employment_type=etype, weekly_hours=hours,
                pref_day=pref_day, pref_night=pref_night,
                blocked_weekdays=blocked, max_consecutive_nights=max_nights,
            )
            e.qualifications = quals
            e.locations = locs
            db.add(e)
            return e

        anna = employee("Anna", "Schmidt", 40, [pfk, beat, fai], [wg_sonnenhof],
                        pref_day=Preference.BEVORZUGT)
        ben = employee("Ben", "Weber", 40, [pfk, beat], [wg_sonnenhof],
                       pref_night=Preference.BEVORZUGT)
        clara = employee("Clara", "Fischer", 30, [pfk], [wg_sonnenhof],
                         etype=EmploymentType.TEILZEIT,
                         pref_night=Preference.AUSGESCHLOSSEN, blocked="6")
        david = employee("David", "Becker", 40, [pfk, beat], [wg_sonnenhof, familie_krause])
        emil = employee("Emil", "Wagner", 35, [pfk], [wg_sonnenhof],
                        etype=EmploymentType.TEILZEIT)
        frieda = employee("Frieda", "Hoffmann", 40, [pfk, fai], [wg_sonnenhof],
                          pref_night=Preference.BEVORZUGT, max_nights=3)
        greta = employee("Greta", "Koch", 25, [pfk], [wg_sonnenhof],
                         etype=EmploymentType.TEILZEIT, pref_day=Preference.BEVORZUGT)
        hannes = employee("Hannes", "Richter", 40, [pfk, beat], [wg_sonnenhof])

        ida = employee("Ida", "Klein", 40, [pfk, beat], [familie_krause],
                       pref_day=Preference.BEVORZUGT)
        jonas = employee("Jonas", "Wolf", 40, [pfk], [familie_krause],
                         pref_night=Preference.BEVORZUGT)
        karla = employee("Karla", "Schröder", 30, [pfk], [familie_krause],
                         etype=EmploymentType.TEILZEIT)
        lena = employee("Lena", "Neumann", 35, [pfk, beat], [familie_krause, wg_hafenblick],
                        etype=EmploymentType.TEILZEIT)

        marie = employee("Marie", "Schwarz", 40, [pfk, fai], [wg_hafenblick])
        nora = employee("Nora", "Zimmermann", 40, [pfk], [wg_hafenblick],
                        pref_night=Preference.BEVORZUGT)
        otto = employee("Otto", "Braun", 30, [pfk, beat], [wg_hafenblick],
                        etype=EmploymentType.TEILZEIT, pref_night=Preference.AUSGESCHLOSSEN)
        paula = employee("Paula", "Krüger", 40, [pfk], [wg_hafenblick])
        db.flush()

        # Abwesenheiten im Folgemonat
        today = date.today()
        next_month_year = today.year + (1 if today.month == 12 else 0)
        next_month = (today.month % 12) + 1
        first = date(next_month_year, next_month, 1)
        db.add_all([
            models.Absence(employee_id=clara.id, type=AbsenceType.URLAUB,
                           start_date=first + timedelta(days=6),
                           end_date=first + timedelta(days=13), note="Sommerurlaub"),
            models.Absence(employee_id=jonas.id, type=AbsenceType.FORTBILDUNG,
                           start_date=first + timedelta(days=2),
                           end_date=first + timedelta(days=4),
                           note="Basiskurs Beatmung"),
        ])
        db.commit()

        # Dienstplan für den Folgemonat generieren (ein Standort als Demo)
        plan = SchedulePlan(location_id=familie_krause.id,
                            year=next_month_year, month=next_month)
        db.add(plan)
        db.commit()
        print(f"Generiere Demo-Dienstplan für {familie_krause.name} "
              f"({next_month:02d}/{next_month_year}) …")
        result = service.generate_plan(db, plan, time_limit_seconds=10)
        print(f"  Status: {result.status}, Zuweisungen: {len(result.assignments)}, "
              f"unbesetzt: {sum(n for _, _, n in result.unfilled)}")

        print("Demo-Daten angelegt. Anmeldung: admin@careplan.local / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
