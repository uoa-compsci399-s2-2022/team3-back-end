from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Enum
from werkzeug.security import generate_password_hash
from MTMS.Utils.utils import dateTimeFormat
from MTMS.Utils.enums import StudentDegreeEnum
from MTMS.Models import Base
from MTMS.Models.applications import Application
from MTMS.Models.courses import CourseUser

UsersGroups = Table('users_groups', Base.metadata,
                    Column('userID', ForeignKey('users.id'), primary_key=True),
                    Column('groupID', ForeignKey('groups.groupID'), primary_key=True)
                    )

InviteUserSavedGroups = Table('invite_user_saved_groups', Base.metadata,
                              Column('inviteUserID', ForeignKey('invite_user_saved.id'), primary_key=True),
                              Column('groupID', ForeignKey('groups.groupID'), primary_key=True)
                              )

PermissionGroups = Table('permission_groups', Base.metadata,
                         Column('permissionID', ForeignKey('permission.permissionID'), primary_key=True),
                         Column('groupID', ForeignKey('groups.groupID'), primary_key=True)
                         )


class Users(Base):
    __tablename__ = 'users'
    id = Column(String(255), primary_key=True)
    password = Column(String(1024))
    email = Column(String(255))
    name = Column(String(255))
    upi = Column(String(255))
    auid = Column(Integer)
    currentlyOverseas = Column(Boolean)
    willBackToNZ = Column(Boolean)
    isCitizenOrPR = Column(Boolean)
    haveValidVisa = Column(Boolean)
    enrolDetails = Column(String(255))
    studentDegree = Column(Enum(StudentDegreeEnum))
    haveOtherContracts = Column(Boolean)
    otherContracts = Column(String(1024))
    maximumWorkingHours = Column(Integer)
    academicRecord = Column(String(1024))
    cv = Column(String(1024))
    createDateTime = Column(DateTime)
    groups = relationship('Groups',
                          secondary=UsersGroups,
                          back_populates='users')
    InviteUserSaved = relationship('InviteUserSaved', back_populates='User')

    # StudentProfile = relationship("StudentProfile", back_populates="Users")
    Application = relationship("Application", back_populates="Users", cascade="all, delete-orphan")
    course_users = relationship('CourseUser', back_populates='user', cascade="all, delete-orphan")

    def __init__(self, id=None, password=None, email=None, name=None, createDateTime=None, **kwargs):
        self.id = id
        self.password = generate_password_hash(password)
        self.email = email
        self.name = name
        self.createDateTime = createDateTime
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'groups': [g.groupName for g in self.groups],
            'createDateTime': dateTimeFormat(self.createDateTime)
        }

    def profile_serialize(self):
        if self.studentDegree is not None:
            studentDegree = self.studentDegree.name
        else:
            studentDegree = None

        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'groups': [g.groupName for g in self.groups],
            'upi': self.upi,
            'auid': self.auid,
            'currentlyOverseas': self.currentlyOverseas,
            'willBackToNZ': self.willBackToNZ,
            'isCitizenOrPR': self.isCitizenOrPR,
            'haveValidVisa': self.haveValidVisa,
            'enrolDetails': self.enrolDetails,
            'studentDegree': studentDegree,
            'haveOtherContracts': self.haveOtherContracts,
            'otherContracts': self.otherContracts,
            'maximumWorkingHours': self.maximumWorkingHours
        }


class Groups(Base):
    __tablename__ = 'groups'
    groupID = Column(Integer, primary_key=True)
    groupName = Column(String(255), unique=True)
    users = relationship('Users',
                         secondary=UsersGroups,
                         back_populates='groups')
    permission = relationship('Permission',
                              secondary=PermissionGroups,
                              back_populates='groups')
    InviteUserSaved = relationship('InviteUserSaved', secondary=InviteUserSavedGroups, back_populates='Groups')

    def serialize(self):
        return {
            'groupID': self.groupID,
            'groupName': self.groupName
        }


class Permission(Base):
    __tablename__ = 'permission'
    permissionID = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    groups = relationship('Groups',
                          secondary=PermissionGroups,
                          back_populates='permission')


    def __repr__(self):
        return self.name


class InviteUserSaved(Base):
    __tablename__ = 'invite_user_saved'
    id = Column(Integer, primary_key=True)
    index = Column(Integer)
    userID = Column(String(255))
    email = Column(String(255))
    name = Column(String(255))
    saver_user_id = Column(ForeignKey('users.id'))

    User = relationship("Users", back_populates="InviteUserSaved")
    Groups = relationship("Groups", secondary=InviteUserSavedGroups, back_populates='InviteUserSaved')

    def serialize(self):
        return {
            'index': self.index,
            'email': self.email,
            'name': self.name,
            'userID': self.userID,
            'groups': [g.groupName for g in self.Groups]
        }
