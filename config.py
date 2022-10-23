"""Flask configuration variables."""
from os import environ
from dotenv import load_dotenv

# Load environment variables from file .env, stored in this directory.
load_dotenv()


class Config:
    """Set Flask configuration from .env file."""

    # Flask configuration
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_DEBUG = environ.get('FLASK_DEBUG')
    debug = environ.get('DEBUG')
    DEBUG = False
    if debug.lower().strip() == "true":
        DEBUG = True

    # Database configuration
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    echo_string = environ.get('SQLALCHEMY_ECHO')
    SQLALCHEMY_ECHO = False
    if echo_string.lower().strip() == "true":
        SQLALCHEMY_ECHO = True

    # Restful API
    json_sort_key = environ.get("JSON_SORT_KEYS")
    JSON_SORT_KEYS = False
    if json_sort_key.lower().strip() == "true":
        JSON_SORT_KEYS = True

    # Email
    EMAIL_ACCOUNT = environ.get("EMAIL_ACCOUNT")
    EMAIL_PASSWORD = environ.get("EMAIL_PASSWORD")
    EMAIL_SENDER_NAME = environ.get("EMAIL_SENDER_NAME")
    EMAIL_SERVER_HOST = environ.get("EMAIL_SERVER_HOST")
    EMAIL_SERVER_PORT = environ.get("EMAIL_SERVER_PORT")
    EMAIL_SERVER_SSL_PORT = environ.get("EMAIL_SERVER_SSL_PORT")
    EMAIL_SENDER_ADDRESS = environ.get("EMAIL_SENDER_ADDRESS")

    PROJECT_DOMAIN = environ.get("PROJECT_DOMAIN")

    # Security
    VALIDATION_CODE_EXPIRATION = int(environ.get("VALIDATION_CODE_EXPIRATION"))
    SECRET_KEY = environ.get('SECRET_KEY')
    TOKEN_EXPIRATION = int(environ.get("TOKEN_EXPIRATION"))

    # Flask-APScheduler
    scheduler_api_enabled = environ.get("SCHEDULER_API_ENABLED")
    SCHEDULER_API_ENABLED = False
    if scheduler_api_enabled.lower().strip() == "true":
        SCHEDULER_API_ENABLED = True

    # Sentry
    SENTRY_DSN = environ.get("SENTRY_DSN")

    # Celery
    CELERY_BROKER_URL = environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = environ.get("CELERY_RESULT_BACKEND")

    celery_result_engine_options = environ.get("CELERY_RESULT_ENGINE_OPTIONS")
    CELERY_RESULT_ENGINE_OPTIONS = False
    if celery_result_engine_options.lower().strip() == "true":
        CELERY_RESULT_ENGINE_OPTIONS = True
