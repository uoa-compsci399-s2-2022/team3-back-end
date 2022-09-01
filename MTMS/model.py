import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

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
            'createDateTime': self.createDateTime
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


