"""CarePlan – Mitarbeiter- und Dienstplanverwaltung für die
außerklinische Intensivpflege."""
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import SessionLocal, init_db
from app.auth import ensure_default_admin
from app.routers import auth_routes, dashboard, employees, locations, plans, qualifications


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(title="CarePlan", lifespan=lifespan)

_secret_file = Path(".session_secret")
secret = os.environ.get("SESSION_SECRET")
if not secret:
    if _secret_file.exists():
        secret = _secret_file.read_text().strip()
    else:
        secret = secrets.token_hex(32)
        _secret_file.write_text(secret)
app.add_middleware(SessionMiddleware, secret_key=secret, max_age=60 * 60 * 12)

app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

app.include_router(auth_routes.router)
app.include_router(dashboard.router)
app.include_router(employees.router)
app.include_router(locations.router)
app.include_router(plans.router)
app.include_router(qualifications.router)


@app.exception_handler(404)
async def not_found(request: Request, exc):
    return RedirectResponse("/", status_code=303)
