"""Page routes for the Flask web app."""

from flask import Blueprint, current_app, render_template, request

from services.prediction_service import get_recent_predictions

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    """Render the dashboard page."""
    return render_template("index.html")


@pages_bp.route("/history")
def history():
    """Render the prediction history page."""
    search_query = request.args.get("search", "").strip()
    sort_order = request.args.get("sort", "desc").strip().lower()

    if sort_order not in {"asc", "desc"}:
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
