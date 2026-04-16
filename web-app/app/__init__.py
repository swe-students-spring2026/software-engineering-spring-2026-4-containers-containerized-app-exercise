"""
Initializes the Flask application and registers all blueprints for routing.
"""

from flask import Flask


def create_app():
    """
    Creates and configures the Flask application.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    from .routes import main
    app.register_blueprint(main)
    return app
