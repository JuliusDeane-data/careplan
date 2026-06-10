"""Einfache Session-Authentifizierung mit PBKDF2-Passwort-Hashes."""
import hashlib
import hmac
import os
import secrets

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), _ITERATIONS
    ).hex()
    return f"pbkdf2${_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _algo, iterations, salt, digest = stored.split("$")
        check = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
        ).hex()
        return hmac.compare_digest(check, digest)
    except (ValueError, TypeError):
        return False


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    user_id = request.session.get("user_id")
    if user_id:
        user = db.get(models.User, user_id)
        if user and user.is_active:
            return user
    raise HTTPException(status_code=303, headers={"Location": "/login"})


def ensure_default_admin(db: Session) -> None:
    """Legt beim ersten Start einen Admin-Benutzer an, falls keiner existiert."""
    if db.query(models.User).count() > 0:
        return
    email = os.environ.get("ADMIN_EMAIL", "admin@careplan.local")
    password = os.environ.get("ADMIN_PASSWORD", "admin123")
    db.add(models.User(
        email=email,
        name="Administrator",
        password_hash=hash_password(password),
        role=models.Role.ADMIN,
    ))
    db.commit()
    print(f"[careplan] Admin-Benutzer angelegt: {email} / {password}")


def flash(request: Request, message: str, category: str = "success") -> None:
    request.session.setdefault("flashes", []).append(
        {"message": message, "category": category}
    )
    # Session-Middleware erkennt In-Place-Änderungen zuverlässig, wenn der
    # Schlüssel neu gesetzt wird.
    request.session["flashes"] = request.session["flashes"]


def pop_flashes(request: Request) -> list[dict]:
    return request.session.pop("flashes", [])
