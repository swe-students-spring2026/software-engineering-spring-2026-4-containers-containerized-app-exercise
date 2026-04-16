"""Application entry point for the Flask web app."""

from flask import Flask

from config import Config
from routes.api import api_bp
from routes.game_api import game_bp
from routes.pages import pages_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    flask_app.register_blueprint(pages_bp)
    flask_app.register_blueprint(api_bp, url_prefix="/api")
    flask_app.register_blueprint(game_bp, url_prefix="/api/game")

    return flask_app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=app.config["DEBUG"])
