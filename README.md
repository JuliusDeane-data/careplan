# CarePlan – Dienstplanung für die außerklinische Intensivpflege

Mitarbeiter- und Dienstplanverwaltung für ambulante Intensivpflegedienste:
Mitarbeiter mit Qualifikationen, Wochenstunden und Dienst-Präferenzen verwalten,
Standorte (Wohngemeinschaften / 1:1-Versorgungen) anlegen, Teams zuweisen und
Monatsdienstpläne **automatisch** unter Einhaltung des Arbeitszeitgesetzes
generieren lassen.

## Schnellstart

```bash
pip install -r requirements.txt
python seed.py            # optional: Demo-Daten + Beispiel-Dienstplan
uvicorn app.main:app      # läuft auf http://127.0.0.1:8000
```

Anmeldung (wird beim ersten Start automatisch angelegt):
**admin@careplan.local** / **admin123**
(änderbar über die Umgebungsvariablen `ADMIN_EMAIL` / `ADMIN_PASSWORD`).

Tests:

```bash
pytest
```

## Tech-Stack

| Schicht   | Technologie                                            |
|-----------|--------------------------------------------------------|
| Backend   | Python 3.11, FastAPI, SQLAlchemy 2.0                   |
| Datenbank | SQLite (per `DATABASE_URL` auf PostgreSQL umstellbar)  |
| Solver    | Google OR-Tools **CP-SAT** (Constraint Programming)    |
| Frontend  | Server-gerendertes Jinja2 + eigenes CSS, kein Build    |

Bewusst schlank gehalten: keine Docker-Pflicht, keine Frontend-Pipeline,
ein einziger Prozess. Für ein Planungsteam von Pflegedienst-Größe
(typisch < 50 gleichzeitige Nutzer) völlig ausreichend.

## Fachliches Modell

- **Mitarbeiter** – Qualifikationen, Beschäftigungsart, Wochenstunden,
  bevorzugte/ausgeschlossene Dienstarten (Tag/Nacht), gesperrte Wochentage,
  persönliche Obergrenzen (Folgetage, Folgenächte), Abwesenheiten
  (Urlaub, Krankheit, Fortbildung).
- **Standorte** – Versorgungen mit eigenen **Diensten** (z. B. Tagdienst
  08–20 Uhr, Nachtdienst 20–08 Uhr), je Dienst Besetzungsstärke und optional
  eine erforderliche Qualifikation. Mitarbeiter werden Standorten zugewiesen.
- **Dienstpläne** – ein Plan je Standort und Monat. Automatische Generierung,
  manuelle Nachbearbeitung im Raster (manuelle Einträge werden „gepinnt“ und
  bei Neuplanung beibehalten), Veröffentlichung, Stundenkonto je Mitarbeiter.

## Automatische Dienstplanung

Der CP-SAT-Solver garantiert **harte Regeln** (werden nie verletzt):

- Mindestens **11 Stunden Ruhezeit** zwischen zwei Diensten (§5 ArbZG)
- Max. **60 Stunden in jedem 7-Tage-Fenster** (Spitzengrenze EU-Arbeitszeit-
  richtlinie; ab 48h wird zusätzlich gewarnt, weil Ausgleich nötig ist)
- Max. **6 Arbeitstage in Folge**, max. **4 Nachtdienste in Folge**
  (je Mitarbeiter weiter einschränkbar)
- Monatssoll (Wochenstunden × Monatslänge) wird um höchstens **12 h
  Mehrarbeit** überschritten
- Max. ein Dienst pro Tag – **auch standortübergreifend**: Dienste an anderen
  Standorten blockieren Tag, Ruhezeit und Stundenkonto
- Qualifikationsanforderungen, Abwesenheiten, ausgeschlossene Dienstarten und
  gesperrte Wochentage
- Einzeldienste über 12 h können gar nicht erst angelegt werden
  (12-h-Dienste sind in der außerklinischen Intensivpflege über tarifliche
  Öffnungsklauseln nach §7 ArbZG üblich)

**Weiche Ziele** (Optimierung, absteigend gewichtet):

1. Möglichst keine unbesetzten Dienste (Unterbesetzung wird ausgewiesen,
   nie durch Regelbrüche „gelöst“)
2. Plan-Stunden möglichst nah am vertraglichen Monatssoll
3. Bevorzugte Dienstarten der Mitarbeiter
4. Faire, zum Stundensoll proportionale Verteilung der Wochenenddienste
5. Mindestens ein komplett freies Wochenende pro Monat

Dieselben Regeln laufen als **Validierung** über jeden Plan: manuelle
Änderungen, die Regeln verletzen, werden im Raster rot markiert und im
Prüfbericht (mit Paragraphenbezug) aufgelistet – so behält die Planung die
Entscheidungshoheit, sieht aber jederzeit die Konsequenzen.

## Projektstruktur

```
app/
├── main.py              # FastAPI-App, Session-Middleware, Startup
├── models.py            # SQLAlchemy-Modelle (Mitarbeiter, Standorte, Pläne …)
├── database.py          # Engine/Session, DATABASE_URL-Konfiguration
├── auth.py              # Login, PBKDF2-Hashes, Flash-Messages
├── scheduling/
│   ├── rules.py         # ArbZG-Regelwerk: Grenzwerte + Verstoß-Prüfung
│   ├── solver.py        # CP-SAT-Modell (OR-Tools)
│   └── service.py       # DB ↔ Solver/Validierung, Stundenkonten
├── routers/             # Web-Routen (Mitarbeiter, Standorte, Pläne …)
├── templates/           # Jinja2-Templates (deutschsprachige UI)
└── static/              # CSS + minimales JS
tests/                   # Regelwerk-, Solver- und Web-Tests (pytest)
seed.py                  # Demo-Daten inkl. generiertem Beispielplan
```

## Bekannte Grenzen / nächste Schritte

- Gesetzliche Feiertage werden noch nicht gesondert behandelt (Zuschläge,
  Ersatzruhetage nach §11 ArbZG).
- Mitarbeitende haben keinen eigenen Login (Self-Service für Tauschwünsche,
  Urlaubsanträge).
- PDF-/Excel-Export der Pläne.
- Bei Wechsel auf PostgreSQL: `DATABASE_URL` setzen und `psycopg` installieren;
  Migrationen (Alembic) sind noch nicht eingerichtet, `init_db()` erstellt das
  Schema beim Start.
