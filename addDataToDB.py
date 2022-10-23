from MTMS.Models.users import Permission, Groups
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def DML(session):
    # Add your DML code here
    # Example:
    # SettingPerm = Permission(name="Setting")
    #
    # adminGroup = session.query(Groups).filter(Groups.groupName == "admin").one_or_none()
    # tutorCoordinator = session.query(Groups).filter(Groups.groupName == "tutorCoordinator").one_or_none()
    # courseCoordinator = session.query(Groups).filter(Groups.groupName == "courseCoordinator").one_or_none()
    # markerCoordinator = session.query(Groups).filter(Groups.groupName == "markerCoordinator").one_or_none()
    #
    # SettingPerm.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    #
    # session.add_all([SettingPerm])
    # session.commit()
    SendingStatus = Permission(name="SendingStatus")
    adminGroup = session.query(Groups).filter(Groups.groupName == "admin").one_or_none()
    tutorCoordinator = session.query(Groups).filter(Groups.groupName == "tutorCoordinator").one_or_none()
    courseCoordinator = session.query(Groups).filter(Groups.groupName == "courseCoordinator").one_or_none()
    markerCoordinator = session.query(Groups).filter(Groups.groupName == "markerCoordinator").one_or_none()

    SendingStatus.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]

    session.add_all([SendingStatus])
    session.commit()





# ---------------------------------------- #
# --- Do not change the following code --- #
# ---------------------------------------- #
def main():
    database_uri = Config.SQLALCHEMY_DATABASE_URI
    database_echo = False
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
    session = session_factory()
    DML(session)


if __name__ == '__main__':
    main()
