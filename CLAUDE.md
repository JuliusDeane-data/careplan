# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CarePlan is an employee and shift scheduling system for outpatient intensive care services (außerklinische Intensivpflege). It manages employees (qualifications, contract hours, shift preferences/exclusions, absences), care locations with their shift definitions, and generates monthly shift plans automatically under German labor law constraints (ArbZG).

**Tech stack:** Python 3.11 + FastAPI + SQLAlchemy 2.0 + SQLite, Google OR-Tools CP-SAT for schedule optimization, server-rendered Jinja2 frontend (German UI) with plain CSS — no build pipeline, no Docker required.

## Commands

```bash
pip install -r requirements.txt   # install dependencies
uvicorn app.main:app --reload     # run dev server on :8000
python seed.py                    # create demo data + sample generated plan
pytest                            # run all tests
pytest tests/test_solver.py -k qualification   # run a single test
```

Default login (auto-created on first start): `admin@careplan.local` / `admin123` (override via `ADMIN_EMAIL` / `ADMIN_PASSWORD`). Database defaults to `sqlite:///./careplan.db`, override via `DATABASE_URL`.

## Architecture

- `app/models.py` — all SQLAlchemy models. Key concepts: `Employee` (with prefs `pref_day`/`pref_night` of enum `Preference`, `blocked_weekdays` as comma-separated weekday ints, personal limits), `Location` with `ShiftTemplate`s (category TAG/NACHT, times, `staff_needed`, optional required qualification), `SchedulePlan` (unique per location+month) containing `ShiftAssignment`s. Assignments with `pinned=True` were set manually and survive regeneration.
- `app/scheduling/rules.py` — **single source of truth for labor law limits** (11h rest, 60h/7-day hard cap with 48h warn, max consecutive days/nights, monthly overtime cap, max 12h shift length) and `find_violations()` which checks a list of `ShiftInfo` per employee. Used by both validation and tests.
- `app/scheduling/solver.py` — pure CP-SAT model, no DB access. Takes `SlotSpec`/`EmployeeSpec` dataclasses, returns `SolveResult`. Hard constraints mirror rules.py; soft objectives: coverage ≫ hours-target deviation > preferences > weekend fairness > one free weekend.
- `app/scheduling/service.py` — bridges DB and solver/rules: collects cross-location assignments of the same employees (`_other_assignments`, ±7 days window) so rest/consecutive/hours checks work across plans; replaces non-pinned assignments after a solve; computes plan summaries.
- `app/routers/` — server-rendered routes (German URLs: `/mitarbeiter`, `/standorte`, `/dienstplaene`, `/qualifikationen`). All require login via `get_current_user` dependency (303 redirect to `/login`).
- Templates in `app/templates/`, flash messages via session (`app/auth.py: flash`).

## Conventions

- UI texts and URLs are German; code identifiers, comments and docstrings follow the existing mixed style (German domain docstrings are fine).
- Any change to scheduling constraints must be made in **both** `rules.py` (validation) and `solver.py` (generation) and covered by a test in `tests/test_solver.py` that validates solver output via `rules.find_violations` (see `validate()` helper there).
- Tests use a throwaway SQLite DB via `DATABASE_URL` env var set before importing `app.main` (see `tests/test_app.py`).
