from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, CheckConstraint, Enum, Table
from MTMS.Models import Base
from MTMS.Utils.utils import dateTimeFormat, CourseApplicationStatus, StudentDegreeEnum

# ApplicationStudentProfile = Table('application_student_profile', Base.metadata,
#                                   Column('ApplicationID', ForeignKey('application.ApplicationID'), primary_key=True),
#                                   Column('StudentProfileID', ForeignKey('student_profile.StudentProfileID'),
#                                          primary_key=True)
#                                   )


class Application(Base):
    __tablename__ = 'application'
    ApplicationID = Column(Integer, primary_key=True)
    createdDateTime = Column(DateTime)
    submittedDateTime = Column(DateTime)
    isCompleted = Column(Boolean, nullable=False)
    studentID = Column(ForeignKey("users.id"))
    Users = relationship("Users", back_populates="Application")
    Courses = relationship("CourseApplication", back_populates="Application")
    SavedProfile = relationship("SavedProfile", back_populates="Application", uselist=False)
    # StudentProfile_R = relationship('StudentProfile',
    #                       secondary=ApplicationStudentProfile,
    #                       back_populates='Applications_R')

    def serialize(self):
        return {
            "application_id": self.ApplicationID,
            "createdDateTime": dateTimeFormat(self.createdDateTime),
            "submittedDateTime": dateTimeFormat(self.submittedDateTime),
            "isCompleted": self.isCompleted
        }


class CourseApplication(Base):
    __tablename__ = 'course_application'
    ApplicationID = Column(ForeignKey("application.ApplicationID"), primary_key=True)
    courseID = Column(ForeignKey("course.courseID"), primary_key=True)
    hasLearned = Column(Boolean)
    grade = Column(String(255))
    explanation = Column(String(1024))
    preExperience = Column(String(1024))
    status = Column(Enum(CourseApplicationStatus))
    resultMesg = Column(String(1024))

    Course = relationship('Course', back_populates='Applications')
    Application = relationship('Application', back_populates='Courses')


class SavedProfile(Base):
    __tablename__ = 'saved_profile'
    applicationID = Column(ForeignKey("application.ApplicationID"), primary_key=True)
    savedTime = Column(DateTime)
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

    Application = relationship('Application', back_populates='SavedProfile')

# class Validation_code(Base):
#     __tablename__ = 'validation_code'
#     Validation_codeID = Column(Integer, primary_key=True)
#     code = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False)
#
#     def __init__(self, code=None, email=None):
#         self.code = code
#         self.email = email

