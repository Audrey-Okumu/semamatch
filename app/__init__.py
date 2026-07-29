import os
from flask import Flask
from app.models.db import db


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(app.instance_path, 'semamatch.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["AT_USERNAME"] = os.environ.get("AT_USERNAME", "sandbox")
    app.config["AT_API_KEY"] = os.environ.get("AT_API_KEY", "")
    app.config["AT_VOICE_NUMBER"] = os.environ.get("AT_VOICE_NUMBER", "")
    app.config["AT_SENDER_ID"] = os.environ.get("AT_SENDER_ID", "")
    app.config["HOLD_MUSIC_URL"] = os.environ.get("HOLD_MUSIC_URL", "")

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    with app.app_context():
        from app.routes.voice import voice_bp
        from app.routes.dashboard import dashboard_bp

        app.register_blueprint(voice_bp)
        app.register_blueprint(dashboard_bp)

        db.create_all()

    return app