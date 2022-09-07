from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Enum
from werkzeug.security import generate_password_hash
from MTMS.utils.utils import ProfileTypeEnum
from MTMS.Models import Base
from MTMS.Models.applications import Application
from MTMS.Models.courses import CourseUser

UsersGroups = Table('UsersGroups', Base.metadata,
                      Column('userID', ForeignKey('Users.id'), primary_key=True),
                      Column('groupID', ForeignKey('Groups.groupID'), primary_key=True)
                      )

PermissionGroups = Table('PermissionGroups', Base.metadata,
                      Column('permissionID', ForeignKey('Permission.permissionID'), primary_key=True),
                      Column('groupID', ForeignKey('Groups.groupID'), primary_key=True)
                      )


class Users(Base):
    __tablename__ = 'Users'
    id = Column(String, primary_key=True)
    password = Column(String)
    email = Column(String)
    name = Column(String)
    createDateTime = Column(DateTime)
    groups = relationship('Groups',
                            secondary=UsersGroups,
                            back_populates='users')
    StudentProfile = relationship("StudentProfile", back_populates="Users")
    Application = relationship("Application", back_populates="Users")
    course_users = relationship('CourseUser', back_populates='user_id')

    def __init__(self, id=None, password=None, email=None, name=None, createDateTime=None):
        self.id = id
        self.password = generate_password_hash(password)
        self.email = email
        self.name = name
        self.createDateTime = createDateTime

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'groups': [g.groupName for g in self.groups],
            'createDateTime': self.createDateTime.isoformat()
        }

    def profile_serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'groups': [g.groupName for g in self.groups]
        }


class Groups(Base):
    __tablename__ = 'Groups'
    groupID = Column(Integer, primary_key=True)
    groupName = Column(String, unique=True)
    users = relationship('Users',
                          secondary=UsersGroups,
                          back_populates='groups')
    permission = relationship('Permission',
                         secondary=PermissionGroups,
                         back_populates='groups')


class Permission(Base):
    __tablename__ = 'Permission'
    permissionID = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    groups = relationship('Groups',
                              secondary=PermissionGroups,
                              back_populates='permission')


class PersonalDetailSetting(Base):
    __tablename__ = 'PersonalDetailSetting'
    profileID = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    Desc = Column(String)
    visibleCondition = Column(String)
    isMultiple = Column(Boolean)
    minimum = Column(Integer)
    maximum = Column(Integer)
    type: ProfileTypeEnum = Column(Enum(ProfileTypeEnum))

    superProfileID = Column(Integer, ForeignKey("PersonalDetailSetting.profileID"), nullable=True)
    subProfile = relationship('PersonalDetailSetting')
    Options = relationship("Options", back_populates="PersonalDetailSetting")
    StudentProfile = relationship("StudentProfile", back_populates="PersonalDetailSetting")

    def serialize(self):
        return {
            'name': self.name,
            'Desc': self.Desc,
            'subProfile': [p.serialize() for p in self.subProfile],
            'visibleCondition': self.visibleCondition,
            'type': str(self.type),
            'isMultiple': self.isMultiple,
            'minimum': self.minimum,
            'maximum': self.maximum,
            'Options': [o.value for o in self.Options]
        }



class Options(Base):
    __tablename__ = 'Options'
    profileID = Column(Integer, ForeignKey("PersonalDetailSetting.profileID"), primary_key=True)
    PersonalDetailSetting = relationship("PersonalDetailSetting", back_populates="Options")

    value = Column(String)


class StudentProfile(Base):
    __tablename__ = 'StudentProfile'
    StudentProfileID = Column(Integer, primary_key=True)
    dateTime = Column(DateTime, nullable=False)
    value = Column(String)

    profileID = Column(ForeignKey("PersonalDetailSetting.profileID"))
    PersonalDetailSetting = relationship("PersonalDetailSetting", back_populates="StudentProfile")

    studentID = Column(ForeignKey("Users.id"))
    Users = relationship("Users", back_populates="StudentProfile")


