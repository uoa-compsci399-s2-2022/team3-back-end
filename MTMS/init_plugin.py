from flasgger import Swagger
from flask_caching import Cache
from flask_cors import CORS
from flask_apscheduler import APScheduler
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def config_swagger_by_flasgger(app):
    app.config['SWAGGER'] = {
        'title': 'MTMS Backend API',
        'version': 'V0.9',
        "description": "Marker & Tutor Management System - One COMPSCI399 Project<br><br>Yogurt Software - Team 3<br>The University of Auckland",
        "termsOfService": "",

    }
    SWAGGER_TEMPLATE = {
        "securityDefinitions": {"APIKeyHeader": {"type": "apiKey", "name": "Authorization", "in": "header"}}}
    swag = Swagger(app, template=SWAGGER_TEMPLATE)
    return swag


def config_caching(app):
    config = {
        "CACHE_TYPE": "FileSystemCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 0,
        "CACHE_DIR": "flask-cache",
    }
    # tell Flask to use the above defined config
    app.config.from_mapping(config)
    cache = Cache(app)
    cache.set("overdue_token", [])
    cache.set("email_validation_code", [])
    return cache


def config_cors(app):
    CORS(app)


def config_APScheduler(app):
    # initialize scheduler
    scheduler = APScheduler()
    if app.config.get('SCHEDULER_API_ENABLED') is None:
        scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
    return scheduler


def config_sentry(app):
    sentry_sdk.init(
        dsn=app.config.get('SENTRY_DSN'),
        integrations=[
            FlaskIntegration(),
        ],

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0
    )