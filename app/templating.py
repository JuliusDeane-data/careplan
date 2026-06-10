"""Jinja2-Konfiguration mit deutschen Format-Filtern."""
from datetime import date
from pathlib import Path

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

WEEKDAYS_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
MONTH_NAMES = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
    "August", "September", "Oktober", "November", "Dezember",
]


def format_date(value: date) -> str:
    return value.strftime("%d.%m.%Y")


def weekday_short(value: date) -> str:
    return WEEKDAYS_SHORT[value.weekday()]


def month_name(month: int) -> str:
    return MONTH_NAMES[month]


def hours(minutes: int | float) -> str:
    return f"{minutes / 60:.1f}".replace(".", ",")


def signed_hours(minutes: int | float) -> str:
    h = minutes / 60
    return f"{'+' if h >= 0 else ''}{h:.1f}".replace(".", ",")


templates.env.filters["d"] = format_date
templates.env.filters["wd"] = weekday_short
templates.env.filters["monthname"] = month_name
templates.env.filters["hours"] = hours
templates.env.filters["signed_hours"] = signed_hours
