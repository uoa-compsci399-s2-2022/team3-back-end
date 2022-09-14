from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, CheckConstraint, Enum, Table
from MTMS.Models import Base
from MTMS.Utils.utils import dateTimeFormat, CourseApplicationStatus

ApplicationStudentProfile = Table('ApplicationStudentProfile', Base.metadata,
                                  Column('ApplicationID', ForeignKey('Application.ApplicationID'), primary_key=True),
                                  Column('StudentProfileID', ForeignKey('StudentProfile.StudentProfileID'),
                                         primary_key=True)
                                  )


class Application(Base):
    __tablename__ = 'Application'
    ApplicationID = Column(Integer, primary_key=True)
    createdDateTime = Column(DateTime)
    submittedDateTime = Column(DateTime)
    isCompleted = Column(Boolean, nullable=False)
    studentID = Column(ForeignKey("Users.id"))
    Users = relationship("Users", back_populates="Application")
    Courses = relationship("CourseApplication", back_populates="Application")
    StudentProfile_R = relationship('StudentProfile',
                          secondary=ApplicationStudentProfile,
                          back_populates='Applications_R')

    def serialize(self):
        return {
            "application_id": self.ApplicationID,
            "createdDateTime": dateTimeFormat(self.createdDateTime),
            "submittedDateTime": dateTimeFormat(self.submittedDateTime),
            "isCompleted": self.isCompleted
        }


class CourseApplication(Base):
    __tablename__ = 'CourseApplication'
    ApplicationID = Column(ForeignKey("Application.ApplicationID"), primary_key=True)
    courseID = Column(ForeignKey("Course.courseID"), primary_key=True)
    hasLearned = Column(Boolean)
    grade = Column(String)
    explanation = Column(String)
    preExperience = Column(String)
    status = Column(Enum(CourseApplicationStatus))
    resultMesg = Column(String)

    Course = relationship('Course', back_populates='Applications')
    Application = relationship('Application', back_populates='Courses')
