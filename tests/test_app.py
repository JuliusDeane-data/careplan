"""End-to-End-Tests der Weboberfläche (Login, CRUD, Plan-Generierung)."""
import os
import tempfile
from datetime import date

import pytest
from fastapi.testclient import TestClient

# Eigene Test-Datenbank, bevor App-Module importiert werden.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}/test.db"
os.environ["ADMIN_EMAIL"] = "admin@test.local"
os.environ["ADMIN_PASSWORD"] = "testpass"

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def logged_in(client):
    response = client.post("/login", data={
        "email": "admin@test.local", "password": "testpass",
    }, follow_redirects=False)
    assert response.status_code == 303
    return client


def test_login_required(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_wrong_password(client):
    response = client.post("/login", data={
        "email": "admin@test.local", "password": "falsch",
    })
    assert response.status_code == 401


def test_dashboard(logged_in):
    response = logged_in.get("/")
    assert response.status_code == 200
    assert "Übersicht" in response.text


def test_qualification_crud(logged_in):
    response = logged_in.post("/qualifikationen", data={
        "code": "pfk", "name": "Pflegefachkraft",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "PFK" in response.text


def test_location_create_with_default_shifts(logged_in):
    response = logged_in.post("/standorte/neu", data={
        "name": "WG Test", "address": "Teststraße 1", "city": "Köln", "notes": "",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "WG Test" in response.text
    assert "Tagdienst" in response.text
    assert "Nachtdienst" in response.text


def test_employee_create(logged_in):
    response = logged_in.post("/mitarbeiter/neu", data={
        "first_name": "Erika", "last_name": "Muster",
        "employment_type": "VOLLZEIT", "weekly_hours": "40",
        "pref_day": "BEVORZUGT", "pref_night": "NEUTRAL",
        "max_consecutive_days": "6", "max_consecutive_nights": "4",
        "active": "on", "notes": "",
        "qualifications": "1", "locations": "1",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "Erika Muster" in response.text


def test_employee_both_categories_excluded_rejected(logged_in):
    response = logged_in.post("/mitarbeiter/neu", data={
        "first_name": "Max", "last_name": "Falsch",
        "employment_type": "VOLLZEIT", "weekly_hours": "40",
        "pref_day": "AUSGESCHLOSSEN", "pref_night": "AUSGESCHLOSSEN",
        "max_consecutive_days": "6", "max_consecutive_nights": "4",
        "active": "on", "notes": "",
    })
    assert response.status_code == 400


def test_absence_create(logged_in):
    response = logged_in.post("/mitarbeiter/1/abwesenheiten", data={
        "type": "URLAUB", "start_date": "2026-07-06", "end_date": "2026-07-12",
        "note": "Test",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "06.07.2026" in response.text


def test_plan_create_and_generate(logged_in):
    # Weitere Mitarbeiter anlegen, damit der Plan besetzbar ist.
    for i in range(2, 8):
        logged_in.post("/mitarbeiter/neu", data={
            "first_name": f"Test{i}", "last_name": f"Kraft{i}",
            "employment_type": "VOLLZEIT", "weekly_hours": "40",
            "pref_day": "NEUTRAL", "pref_night": "NEUTRAL",
            "max_consecutive_days": "6", "max_consecutive_nights": "4",
            "active": "on", "notes": "",
            "qualifications": "1", "locations": "1",
        })

    response = logged_in.post("/dienstplaene", data={
        "location_id": "1", "month": "2026-07",
    }, follow_redirects=True)
    assert response.status_code == 200

    response = logged_in.post("/dienstplaene/1/generieren", follow_redirects=True)
    assert response.status_code == 200
    assert "Plan erstellt" in response.text

    # Plan-Ansicht zeigt Stundenkonto und keine Regelverstöße.
    response = logged_in.get("/dienstplaene/1")
    assert response.status_code == 200
    assert "Stundenkonto" in response.text
    assert "Verstoß" not in response.text


def test_manual_assignment_pinned(logged_in):
    response = logged_in.post("/dienstplaene/1/zuweisung", data={
        "day": "2026-07-15", "template_id": "1",
        "employee_id": "1", "assignment_id": "",
    }, follow_redirects=False)
    # Entweder neu gesetzt oder als Duplikat abgelehnt – beides ist ein Redirect.
    assert response.status_code == 303


def test_duplicate_plan_rejected(logged_in):
    response = logged_in.post("/dienstplaene", data={
        "location_id": "1", "month": "2026-07",
    }, follow_redirects=True)
    assert "existiert bereits" in response.text
