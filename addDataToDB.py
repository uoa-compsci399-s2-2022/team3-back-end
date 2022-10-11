from MTMS.Models.users import Permission, Groups
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def DML(session):
    InviteStudent = Permission(name="InviteStudent")
    InviteCC = Permission(name="InviteCC")
    InviteTC = Permission(name="InviteTC")
    InviteMC = Permission(name="InviteMC")

    adminGroup = session.query(Groups).filter(Groups.groupName == "admin").one_or_none()
    tutorCoordinator = session.query(Groups).filter(Groups.groupName == "tutorCoordinator").one_or_none()
    courseCoordinator = session.query(Groups).filter(Groups.groupName == "courseCoordinator").one_or_none()
    markerCoordinator = session.query(Groups).filter(Groups.groupName == "markerCoordinator").one_or_none()

    InviteStudent.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    InviteCC.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    InviteTC.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    InviteMC.groups = [adminGroup, tutorCoordinator, markerCoordinator]

    session.add_all([InviteStudent, InviteCC, InviteTC, InviteMC])
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
    session_factory = sessionmaker(autocommit=False, autoflush=True, bind=database_engine)
    session = session_factory()
    DML(session)


if __name__ == '__main__':
    main()
