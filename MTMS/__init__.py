import sqlalchemy.exc
from flask import Flask
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from flask_login import LoginManager
from MTMS.Models.setting import Setting
from MTMS.Models.users import Base
from MTMS.create_env_config import create_env
from MTMS.databaseDefaultValue import set_default_value
from MTMS.Models import Base

from MTMS.init_plugin import config_swagger_by_flasgger, config_caching, config_cors, config_APScheduler, config_sentry

db_session: scoped_session = None
login_manager = LoginManager()
cache = None
scheduler = None


def create_app():
    global db_session, cache, scheduler
    create_env()
    app = Flask(__name__)
    app.config.from_object('config.Config')
    scheduler = config_APScheduler(app)
    cache = config_caching(app)
    db_session = config_database(app)
    config_blueprint(app)
    config_swagger_by_flasgger(app)
    config_cors(app)
    config_errorhandler(app)
    if app.config['SENTRY_DSN'].strip() != "":
        config_sentry(app)
    return app


def config_database(app):
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
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=database_engine)

    if len(database_engine.table_names()) == 0:
        print("REPOPULATING DATABASE for SecondHand Plugin ...")
        Base.metadata.create_all(database_engine)
        session = session_factory()
        set_default_value(session)
        print("REPOPULATING DATABASE for SecondHand Plugin ... FINISHED")
    db_session = scoped_session(session_factory)

    if db_session.query(Setting).first() is None:
        db_session.add(Setting())
        db_session.commit()

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
    from MTMS.Term import views
    views.register(app)
    from MTMS.Enrollment import views
    views.register(app)


def config_errorhandler(app):
    @app.errorhandler(sqlalchemy.exc.PendingRollbackError)
    def error_handler(e):
        print("---------------------")
        print("---------------------")
        print(e)
        print("---------------------")
        print("---------------------")
        db_session.rollback()