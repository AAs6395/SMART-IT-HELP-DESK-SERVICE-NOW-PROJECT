"""
config.py
---------
Central place for all configuration values used by the Flask application.
Keeping configuration in one file makes the project easy to read and change.
"""

import os

# Absolute path of the project folder (the folder that contains this file).
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Folder where the SQLite database file lives.
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Folder where uploaded ticket attachments are stored.
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")


def _sqlite_uri(filename="helpdesk.db"):
    """Build a SQLAlchemy SQLite URI that also works on Windows."""
    path = os.path.join(INSTANCE_DIR, filename).replace("\\", "/")
    return "sqlite:///" + path


class Config:
    """Default (development) configuration."""

    # Used by Flask to sign session cookies.
    # In a real deployment set the SECRET_KEY environment variable.
    SECRET_KEY = os.environ.get("SECRET_KEY", "smart-it-helpdesk-dev-secret-key-change-me")

    # Database connection. DATABASE_URL can be set to point somewhere else.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _sqlite_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Load the sample demonstration dataset (seed_data.py) when the ticket
    # table is empty. Set to False for a completely empty help desk.
    SEED_SAMPLE_DATA = True

    # File upload settings
    UPLOAD_FOLDER = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB maximum upload size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "txt", "doc", "docx", "log", "zip"}

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
