from flask import Flask, g
from sqlalchemy.orm import sessionmaker, clear_mappers, scoped_session, class_mapper
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from flask_login import LoginManager, current_user
from .model import Base, User
from flask_apispec import FlaskApiSpec
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_caching import Cache


db_session = None
login_manager = LoginManager()
cache = None


def create_app():
    global db_session, cache
    app = Flask(__name__)
    app.config.from_object('config.Config')
    cache = config_caching(app)
    db_session = config_database(app)
    swagger_docs = config_swagger(app)
    config_blueprint(app, swagger_docs)
    return app


def config_database(app):
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    database_echo = app.config.get('SQLALCHEMY_ECHO', False)
    database_engine = create_engine(database_uri,
                                    connect_args={"check_same_thread": False},
                                    poolclass=QueuePool,
                                    pool_pre_ping=True,
                                    echo=database_echo)
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
    if len(database_engine.table_names()) == 0:
        print("REPOPULATING DATABASE for SecondHand Plugin ...")
        Base.metadata.create_all(database_engine)
        print("REPOPULATING DATABASE for SecondHand Plugin ... FINISHED")
    db_session = scoped_session(session_factory)
    return db_session



def config_blueprint(app, swagger_docs):
    from MTMS.Sample import views
    views.register(app, swagger_docs)
    from MTMS.Auth import views
    views.register(app, swagger_docs)


def config_swagger(app):
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='MTMS Backend API',
            version='v0',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0.0',
            info={"description": "Marker & Tutor Management System - One COMPSCI399 Project<br><br>The University of Auckland"}

        ),
        'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
    })
    docs = FlaskApiSpec(app)
    return docs


def config_caching(app):
    config = {
        "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 0
    }
    # tell Flask to use the above defined config
    app.config.from_mapping(config)
    cache = Cache(app)
    cache.set("overdue_token", [])
    return cache

