from flask import current_app
from sqlalchemy import create_engine

from .model import Base


def init_db(app):
    """Create one engine per application and initialize missing tables."""
    engine = create_engine(app.config["DATABASE_URL"], echo=False)
    Base.metadata.create_all(engine)
    app.extensions["database_engine"] = engine


def get_engine():
    return current_app.extensions["database_engine"]
