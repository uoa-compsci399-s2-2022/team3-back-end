from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Table, Enum
from werkzeug.security import generate_password_hash
from MTMS.Utils.utils import StudentDegreeEnum, dateTimeFormat
from MTMS.Models import Base
from MTMS.Models.applications import Application
from MTMS.Models.courses import CourseUser

UsersGroups = Table('users_groups', Base.metadata,
                      Column('userID', ForeignKey('users.id'), primary_key=True),
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
    maximumWorkHours = Column(Integer)
    academicRecord = Column(String(1024))
    cv = Column(String(1024))
    createDateTime = Column(DateTime)
    groups = relationship('Groups',
                            secondary=UsersGroups,
                            back_populates='users')

    # StudentProfile = relationship("StudentProfile", back_populates="Users")
    Application = relationship("Application", back_populates="Users")
    course_users = relationship('CourseUser', back_populates='user')

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
            'createDateTime': dateTimeFormat(self.createDateTime)
        }

    def profile_serialize(self):
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
            'studentDegree': self.studentDegree,
            'haveOtherContracts': self.haveOtherContracts,
            'otherContracts': self.otherContracts,
            'maximumWorkHours': self.maximumWorkHours
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


class Permission(Base):
    __tablename__ = 'permission'
    permissionID = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    groups = relationship('Groups',
                              secondary=PermissionGroups,
                              back_populates='permission')

#
# class PersonalDetailSetting(Base):
#     __tablename__ = 'personal_detail_setting'
#     profileID = Column(Integer, primary_key=True)
#     name = Column(String(255), nullable=False)
#     Desc = Column(String(255))
#     visibleCondition = Column(String(255))
#     isMultiple = Column(Boolean)
#     minimum = Column(Integer)
#     maximum = Column(Integer)
#     type: ProfileTypeEnum = Column(Enum(ProfileTypeEnum))
#
#     superProfileID = Column(Integer, ForeignKey("personal_detail_setting.profileID"), nullable=True)
#     subProfile = relationship('PersonalDetailSetting')
#     Options = relationship("Options", back_populates="PersonalDetailSetting")
#     StudentProfile = relationship("StudentProfile", back_populates="PersonalDetailSetting")
#
#     def serialize(self):
#         return {
#             'name': self.name,
#             'Desc': self.Desc,
#             'subProfile': [p.serialize() for p in self.subProfile],
#             'visibleCondition': self.visibleCondition,
#             'type': str(self.type),
#             'isMultiple': self.isMultiple,
#             'minimum': self.minimum,
#             'maximum': self.maximum,
#             'Options': [o.value for o in self.Options]
#         }
#
#
#
# class Options(Base):
#     __tablename__ = 'options'
#     profileID = Column(Integer, ForeignKey("personal_detail_setting.profileID"), primary_key=True)
#     PersonalDetailSetting = relationship("PersonalDetailSetting", back_populates="Options")
#
#     value = Column(String(255))
#
#
# class StudentProfile(Base):
#     __tablename__ = 'student_profile'
#     StudentProfileID = Column(Integer, primary_key=True)
#     dateTime = Column(DateTime, nullable=False)
#     value = Column(String(255))
#
#     profileID = Column(ForeignKey("personal_detail_setting.profileID"))
#     PersonalDetailSetting = relationship("PersonalDetailSetting", back_populates="StudentProfile")
#
#     studentID = Column(ForeignKey("users.id"))
#     Users = relationship("Users", back_populates="StudentProfile")
#
#     Applications_R = relationship('Application',
#                           secondary=ApplicationStudentProfile,
#                           back_populates='StudentProfile_R')
#
#
