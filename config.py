import os
from datetime import timedelta

# APP CONFIGURATION
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.environ.get("FLASK_ENV") == "development"
TESTING = os.environ.get("TESTING", False)

# DATABASE CONFIGURATION
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "sqlite:///temp1.db"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = DEBUG

# SESSION CONFIGURATION
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# MAIL CONFIGURATION
MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", True)
MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", False)
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "noreply@notesapp.com")

# SECURITY CONFIGURATION
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = None

# RATE LIMITING
RATELIMIT_STORAGE_URL = os.environ.get("RATELIMIT_STORAGE_URL", "memory://")

# LOGGING
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE = os.environ.get("LOG_FILE", "app.log")