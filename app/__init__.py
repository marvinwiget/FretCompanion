import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def create_app(test_config=None):
    load_dotenv(PROJECT_ROOT / ".env")
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY"),
        DATABASE_URL=os.getenv("DATABASE_URL") or f"sqlite+pysqlite:///{PROJECT_ROOT / 'fret_companion.db'}",
    )
    if test_config is not None:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("Set FLASK_SECRET_KEY in .env before starting Fret Companion.")

    from .database.session import init_db
    from .routes import pages

    init_db(app)
    app.register_blueprint(pages)
    return app
