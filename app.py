from __future__ import annotations

import csv
import os
import ssl
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_DATABASE_PATH = PROJECT_ROOT / "data" / "rfl_app.db"
SEED_CSV_PATH = PROJECT_ROOT / "data" / "seed_measurements.csv"


def default_database_uri() -> str:
    if os.environ.get("DATABASE_URL"):
        uri = os.environ["DATABASE_URL"]
        parts = urlsplit(uri)
        query_pairs = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "sslmode"]
        uri = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query_pairs), parts.fragment))
        if uri.startswith("postgresql://"):
            return uri.replace("postgresql://", "postgresql+pg8000://", 1)
        if uri.startswith("postgres://"):
            return uri.replace("postgres://", "postgresql+pg8000://", 1)
        return uri
    LOCAL_DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{LOCAL_DATABASE_PATH.as_posix()}"


app = Flask(__name__, static_folder="public", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "rfl-app-local-dev")
app.config["SQLALCHEMY_DATABASE_URI"] = default_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if os.environ.get("DATABASE_URL"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "ssl_context": ssl.create_default_context(),
        }
    }

db = SQLAlchemy(app)


class Measurement(db.Model):
    __tablename__ = "measurements"

    id = db.Column(db.Integer, primary_key=True)
    entry_date = db.Column(db.String(10), nullable=False, index=True)
    weight_lbs = db.Column(db.Float, nullable=False)
    waist_in = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.String(19), nullable=False)
    updated_at = db.Column(db.String(19), nullable=False)


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")


def today_iso_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def display_date(date_text: str) -> str:
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").strftime("%b-%d-%Y")
    except (TypeError, ValueError):
        return date_text


app.jinja_env.filters["display_date"] = display_date


def display_date_range(date_range: str) -> str:
    try:
        start_text, end_text = date_range.split(" to ", 1)
    except (AttributeError, ValueError):
        return date_range
    return f"{display_date(start_text)} to {display_date(end_text)}"


app.jinja_env.filters["display_date_range"] = display_date_range


def init_db() -> None:
    db.create_all()


def seed_if_empty() -> None:
    if Measurement.query.count() > 0 or not SEED_CSV_PATH.exists():
        return

    with SEED_CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            entry_date = (row.get("entry_date") or "").strip()
            weight_text = (row.get("weight_lbs") or "").strip()
            waist_text = (row.get("waist_in") or "").strip()
            notes = (row.get("notes") or "").strip()
            if not entry_date or not weight_text or not waist_text:
                continue
            timestamp = now_iso()
            db.session.add(
                Measurement(
                    entry_date=entry_date,
                    weight_lbs=float(weight_text),
                    waist_in=float(waist_text),
                    notes=notes,
                    created_at=timestamp,
                    updated_at=timestamp,
                )
            )
    db.session.commit()


def validate_measurement_form(form) -> tuple[dict[str, str], list[str]]:
    values = {
        "entry_date": (form.get("entry_date") or "").strip(),
        "weight_lbs": (form.get("weight_lbs") or "").strip(),
        "waist_in": (form.get("waist_in") or "").strip(),
        "notes": (form.get("notes") or "").strip(),
    }
    errors: list[str] = []

    try:
        datetime.strptime(values["entry_date"], "%Y-%m-%d")
    except ValueError:
        errors.append("Entry date must be a valid date in YYYY-MM-DD format.")

    try:
        weight = float(values["weight_lbs"])
        if weight <= 0:
            errors.append("Weight must be greater than zero.")
    except ValueError:
        errors.append("Weight must be a valid number.")

    try:
        waist = float(values["waist_in"])
        if waist <= 0:
            errors.append("Waist must be greater than zero.")
    except ValueError:
        errors.append("Waist must be a valid number.")

    return values, errors


def get_measurements() -> list[Measurement]:
    return Measurement.query.order_by(Measurement.entry_date.asc(), Measurement.id.asc()).all()


def build_chart_points(measurements: list[Measurement]) -> list[dict[str, object]]:
    return [
        {
            "id": row.id,
            "date": row.entry_date,
            "weight": row.weight_lbs,
            "waist": row.waist_in,
            "notes": row.notes,
        }
        for row in measurements
    ]


def build_weekly_chart_points(weekly_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "date": row["label"],
            "weight": row["avg_weight"],
            "waist": row["avg_waist"],
            "notes": row["date_range"],
        }
        for row in sorted(weekly_rows, key=lambda row: row["week_number"])
    ]


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def build_insight_metrics(measurements: list[Measurement]) -> dict[str, object]:
    if not measurements:
        return {
            "seven_day_avg_weight": None,
            "seven_day_avg_waist": None,
            "total_weight_lost": None,
            "total_waist_lost": None,
            "avg_daily_weight_change": None,
            "avg_weekly_weight_change": None,
            "avg_weekly_waist_change": None,
            "lowest_weight": None,
            "lowest_waist": None,
        }

    first = measurements[0]
    latest = measurements[-1]
    trailing_rows = measurements[-7:]
    first_date = datetime.strptime(first.entry_date, "%Y-%m-%d").date()
    latest_date = datetime.strptime(latest.entry_date, "%Y-%m-%d").date()
    elapsed_days = max((latest_date - first_date).days, 1)
    weight_change = latest.weight_lbs - first.weight_lbs
    waist_change = latest.waist_in - first.waist_in
    lowest_weight = min(measurements, key=lambda row: row.weight_lbs)
    lowest_waist = min(measurements, key=lambda row: row.waist_in)

    return {
        "seven_day_avg_weight": average([row.weight_lbs for row in trailing_rows]),
        "seven_day_avg_waist": average([row.waist_in for row in trailing_rows]),
        "total_weight_lost": first.weight_lbs - latest.weight_lbs,
        "total_waist_lost": first.waist_in - latest.waist_in,
        "avg_daily_weight_change": weight_change / elapsed_days,
        "avg_weekly_weight_change": (weight_change / elapsed_days) * 7,
        "avg_weekly_waist_change": (waist_change / elapsed_days) * 7,
        "lowest_weight": lowest_weight,
        "lowest_waist": lowest_waist,
    }


def build_dashboard_context() -> dict[str, object]:
    measurements = get_measurements()
    chart_points = build_chart_points(measurements)

    summary = {
        "row_count": 0,
        "start_date": "",
        "start_weight": "",
        "start_waist": "",
        "latest_date": "",
        "weight_today": "",
        "waist_today": "",
        "weight_change": "",
        "waist_change": "",
    }
    selected_point = chart_points[-1] if chart_points else None

    if measurements:
        first = measurements[0]
        latest = measurements[-1]
        summary = {
            "row_count": len(measurements),
            "start_date": first.entry_date,
            "start_weight": f"{first.weight_lbs:.2f}",
            "start_waist": f"{first.waist_in:.2f}",
            "latest_date": latest.entry_date,
            "weight_today": f"{latest.weight_lbs:.2f}",
            "waist_today": f"{latest.waist_in:.2f}",
            "weight_change": f"{latest.weight_lbs - first.weight_lbs:+.2f}",
            "waist_change": f"{latest.waist_in - first.waist_in:+.2f}",
        }

    return {
        "measurements": measurements,
        "chart_points": chart_points,
        "summary": summary,
        "selected_point": selected_point,
    }


def build_insights_context() -> dict[str, object]:
    measurements = get_measurements()
    insight_metrics = build_insight_metrics(measurements)
    weekly_groups: dict[str, list[Measurement]] = defaultdict(list)

    if not measurements:
        return {
            "weekly_chart_points": [],
            "insight_metrics": insight_metrics,
            "weekly_rows": [],
            "current_week": None,
        }

    first_entry_date = datetime.strptime(measurements[0].entry_date, "%Y-%m-%d").date()
    first_week_start = first_entry_date - timedelta(days=first_entry_date.weekday())

    for measurement in measurements:
        entry_date = datetime.strptime(measurement.entry_date, "%Y-%m-%d").date()
        week_start = entry_date - timedelta(days=entry_date.weekday())
        weekly_groups[week_start.isoformat()].append(measurement)

    weekly_rows: list[dict[str, object]] = []
    for week_start_text, rows in weekly_groups.items():
        sorted_rows = sorted(rows, key=lambda row: row.entry_date)
        week_start = datetime.strptime(week_start_text, "%Y-%m-%d").date()
        week_end = week_start + timedelta(days=6)
        week_number = ((week_start - first_week_start).days // 7) + 1
        start_measurement = sorted_rows[0]
        avg_weight = sum(row.weight_lbs for row in sorted_rows) / len(sorted_rows)
        avg_waist = sum(row.waist_in for row in sorted_rows) / len(sorted_rows)
        weekly_rows.append(
            {
                "week_number": week_number,
                "label": f"Week {week_number}",
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "date_range": f"{week_start.isoformat()} to {week_end.isoformat()}",
                "start_weight": start_measurement.weight_lbs,
                "start_waist": start_measurement.waist_in,
                "avg_weight": avg_weight,
                "avg_waist": avg_waist,
                "entry_count": len(sorted_rows),
            }
        )

    weekly_rows.sort(key=lambda row: row["week_number"], reverse=True)
    current_week = weekly_rows[0] if weekly_rows else None
    weekly_chart_points = build_weekly_chart_points(weekly_rows)

    return {
        "weekly_chart_points": weekly_chart_points,
        "insight_metrics": insight_metrics,
        "weekly_rows": weekly_rows,
        "current_week": current_week,
    }


@app.before_request
def prepare_app() -> None:
    init_db()
    seed_if_empty()


@app.route("/")
def dashboard():
    context = build_dashboard_context()
    return render_template(
        "dashboard.html",
        **context,
        form_values=None,
        form_errors=[],
        default_entry_date=today_iso_date(),
    )


@app.route("/insights")
def insights():
    context = build_insights_context()
    return render_template("insights.html", **context)


@app.route("/measurements", methods=["POST"])
def create_measurement():
    values, errors = validate_measurement_form(request.form)
    if errors:
        context = build_dashboard_context()
        return render_template(
            "dashboard.html",
            **context,
            form_values=values,
            form_errors=errors,
            default_entry_date=today_iso_date(),
        ), 400

    timestamp = now_iso()
    measurement = Measurement(
        entry_date=values["entry_date"],
        weight_lbs=float(values["weight_lbs"]),
        waist_in=float(values["waist_in"]),
        notes=values["notes"],
        created_at=timestamp,
        updated_at=timestamp,
    )
    db.session.add(measurement)
    db.session.commit()
    flash("Measurement added.")
    return redirect(url_for("dashboard"))


@app.route("/measurements/<int:measurement_id>/edit", methods=["GET", "POST"])
def edit_measurement(measurement_id: int):
    measurement = db.session.get(Measurement, measurement_id)
    if measurement is None:
        flash("Measurement not found.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        values, errors = validate_measurement_form(request.form)
        if not errors:
            measurement.entry_date = values["entry_date"]
            measurement.weight_lbs = float(values["weight_lbs"])
            measurement.waist_in = float(values["waist_in"])
            measurement.notes = values["notes"]
            measurement.updated_at = now_iso()
            db.session.commit()
            flash("Measurement updated.")
            return redirect(url_for("dashboard"))
        form_values = values
    else:
        errors = []
        form_values = {
            "entry_date": measurement.entry_date,
            "weight_lbs": f"{measurement.weight_lbs:.2f}",
            "waist_in": f"{measurement.waist_in:.2f}",
            "notes": measurement.notes,
        }

    return render_template(
        "edit_measurement.html",
        measurement=measurement,
        form_values=form_values,
        form_errors=errors,
    )


@app.route("/measurements/<int:measurement_id>/delete", methods=["POST"])
def delete_measurement(measurement_id: int):
    measurement = db.session.get(Measurement, measurement_id)
    if measurement is not None:
        db.session.delete(measurement)
        db.session.commit()
        flash("Measurement deleted.")
    else:
        flash("Measurement not found.")
    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return {"status": "ok"}


with app.app_context():
    init_db()
    seed_if_empty()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
