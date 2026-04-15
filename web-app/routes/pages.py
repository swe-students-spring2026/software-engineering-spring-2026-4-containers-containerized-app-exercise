"""Page routes for the Flask dashboard."""

from flask import Blueprint, current_app, render_template, request
from services.prediction_service import (
    get_latest_prediction,
    get_recent_predictions,
    get_prediction_stats,
)

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Render the main dashboard page."""
    latest = get_latest_prediction()
    recent = get_recent_predictions(current_app.config["RECENT_LIMIT"])
    stats = get_prediction_stats(100)

    return render_template(
        "index.html",
        latest=latest,
        recent=recent,
        stats=stats,
        refresh_ms=current_app.config["DASHBOARD_REFRESH_MS"],
    )


@pages_bp.route("/history")
def history():
    """Render the prediction history page with search and sort options."""
    search_query = request.args.get("search", "").strip()
    sort_order = request.args.get("sort", "desc").strip().lower()

    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    recent = get_recent_predictions(
        limit=current_app.config["RECENT_LIMIT"],
        search_query=search_query,
        sort_order=sort_order,
    )

    return render_template(
        "history.html",
        recent=recent,
        search_query=search_query,
        sort_order=sort_order,
    )
