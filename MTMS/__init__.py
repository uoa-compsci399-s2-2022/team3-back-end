from flask import Flask
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, NullPool
from flask_login import LoginManager
from MTMS.Models.users import Base
from flask_caching import Cache
from flasgger import Swagger
from flask_cors import CORS
from MTMS.databaseDefaultValue import set_default_value
from MTMS.Models import Base

db_session = None
login_manager = LoginManager()
cache = None


def create_app():
    global db_session, cache
    app = Flask(__name__)
    app.config.from_object('config.Config')
    cache = config_caching(app)
    db_session = config_database(app)
    config_blueprint(app)
    config_swagger_by_flasgger(app)
    config_cors(app)

    return app


def config_database(app):
    # database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    # database_echo = app.config.get('SQLALCHEMY_ECHO', False)
    # database_engine = create_engine(database_uri,
    #                                 connect_args={"check_same_thread": False},
    #                                 poolclass=NullPool,
    #                                 pool_pre_ping=True,
    #                                 echo=database_echo)
    # session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
    # if len(database_engine.table_names()) == 0:
    #     print("REPOPULATING DATABASE for SecondHand Plugin ...")
    #     Base.metadata.create_all(database_engine)
    #     session = session_factory()
    #     set_default_value(session)
    #
    #     print("REPOPULATING DATABASE for SecondHand Plugin ... FINISHED")
    # db_session = scoped_session(session_factory)

    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    database_echo = app.config.get('SQLALCHEMY_ECHO', False)
    if database_uri.startswith("sqlite"):
        database_engine = create_engine(database_uri,
                                        pool_pre_ping=True,
                                        poolclass=NullPool,
                                        echo=database_echo,
                                        connect_args={"check_same_thread": False})
    else:
        database_engine = create_engine(database_uri,
                                        pool_pre_ping=True,
                                        echo=database_echo)
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)

    if len(database_engine.table_names()) == 0:
        print("REPOPULATING DATABASE for SecondHand Plugin ...")
        Base.metadata.create_all(database_engine)
        session = session_factory()
        set_default_value(session)
        print("REPOPULATING DATABASE for SecondHand Plugin ... FINISHED")

    db_session = scoped_session(session_factory)
    return db_session


def config_blueprint(app):
    from MTMS.Auth import views
    views.register(app)
    from MTMS.Management import views
    views.register(app)
    from MTMS.Users import views
    views.register(app)
    from MTMS.Application import views
    views.register(app)
    from MTMS.Course import views
    views.register(app)


def config_swagger_by_flasgger(app):
    app.config['SWAGGER'] = {
        'title': 'MTMS Backend API',
        'version': 'v0',
        "description": "Marker & Tutor Management System - One COMPSCI399 Project<br><br>Yogurt Software - Team 3<br>The University of Auckland",
        "termsOfService": ""

    }
    SWAGGER_TEMPLATE = {
        "securityDefinitions": {"APIKeyHeader": {"type": "apiKey", "name": "Authorization", "in": "header"}}}
    swag = Swagger(app, template=SWAGGER_TEMPLATE)
    return swag


def config_caching(app):
    config = {
        "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 0
    }
    # tell Flask to use the above defined config
    app.config.from_mapping(config)
    cache = Cache(app)
    cache.set("overdue_token", [])
    cache.set("email_validation_code", [])
    return cache



def config_cors(app):
    CORS(app)


