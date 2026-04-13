from flask import Flask

from config import Config
from routes import main_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER
    app.config["RUNTIME_FOLDER"] = Config.RUNTIME_FOLDER

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(main_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)