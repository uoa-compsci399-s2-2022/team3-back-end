"""Flask configuration variables."""
from os import environ
from dotenv import load_dotenv

# Load environment variables from file .env, stored in this directory.
load_dotenv()


class Config:
    """Set Flask configuration from .env file."""

    # Flask configuration
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('ENV')
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

    # Security
    SECRET_KEY = environ.get('SECRET_KEY')
    TOKEN_EXPIRATION = environ.get("TOKEN_EXPIRATION")

    # Restful API
    CONFIG_SWAGGER_BY = environ.get("CONFIG_SWAGGER_BY")
    json_sort_key = environ.get("JSON_SORT_KEYS")
    JSON_SORT_KEYS = False
    if json_sort_key.lower().strip() == "true":
        JSON_SORT_KEYS = True
