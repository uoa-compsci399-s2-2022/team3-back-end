from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, CheckConstraint, Enum, Table
from MTMS.Models import Base
from MTMS.Utils.utils import dateTimeFormat, ApplicationStatus, StudentDegreeEnum
from MTMS.Models.courses import Term

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
    studentID = Column(ForeignKey("users.id"))
    term = Column(ForeignKey("term.termID"))

    Term = relationship("Term", back_populates="Applications")
    Users = relationship("Users", back_populates="Application")
    Courses = relationship("CourseApplication", back_populates="Application")
    SavedProfile = relationship("SavedProfile", back_populates="Application", uselist=False)
    status = Column(Enum(ApplicationStatus))
    resultMesg = Column(String(1024))


    def serialize(self):
        return {
            "applicationID": self.ApplicationID,
            "createdDateTime": dateTimeFormat(self.createdDateTime),
            "submittedDateTime": dateTimeFormat(self.submittedDateTime),
            "term": self.Term.termName,
            "termID": self.Term.termID,
            "status": self.status.name
        }


class CourseApplication(Base):
    __tablename__ = 'course_application'
    ApplicationID = Column(ForeignKey("application.ApplicationID"), primary_key=True)
    courseID = Column(ForeignKey("course.courseID"), primary_key=True)
    hasLearned = Column(Boolean)
    grade = Column(String(255))
    explanation = Column(String(1024))
    preExperience = Column(String(1024))
    preference = Column(Integer)

    Course = relationship('Course', back_populates='Applications')
    Application = relationship('Application', back_populates='Courses')

    def serialize(self):
        return {
            "courseID": self.courseID,
            "courseNum": self.Course.courseNum,
            "courseName": self.Course.courseName,
            "hasLearned": self.hasLearned,
            "grade": self.grade,
            "explanation": self.explanation,
            "preExperience": self.preExperience,
            "preference": self.preference
        }



class SavedProfile(Base):
    __tablename__ = 'saved_profile'
    applicationID = Column(ForeignKey("application.ApplicationID"), primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    upi = Column(String(255))
    auid = Column(Integer)
    savedTime = Column(DateTime)
    currentlyOverseas = Column(Boolean)
    willBackToNZ = Column(Boolean)
    isCitizenOrPR = Column(Boolean)
    haveValidVisa = Column(Boolean)
    enrolDetails = Column(String(255))
    studentDegree: StudentDegreeEnum = Column(Enum(StudentDegreeEnum))
    haveOtherContracts = Column(Boolean)
    otherContracts = Column(String(1024))
    maximumWorkingHours = Column(Integer)
    academicRecord = Column(String(1024))
    cv = Column(String(1024))

    Application = relationship('Application', back_populates='SavedProfile')

    def __setattr__(self, key, value):
        if key == 'studentDegree':
            if value in ["Undergraduate","Postgraduate"]:
                super().__setattr__(key, value)
            else:
                raise ValueError("studentDegree must be Undergraduate or Postgraduate")
        else:
            super().__setattr__(key, value)

    def serialize(self):
        if self.studentDegree is not None:
            studentDegree = self.studentDegree.name
        else:
            studentDegree = None

        return {
            'email': self.email,
            'name': self.name,
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
            'maximumWorkingHours': self.maximumWorkingHours,
            'savedTime': dateTimeFormat(self.savedTime)
        }

# class Validation_code(Base):
#     __tablename__ = 'validation_code'
#     Validation_codeID = Column(Integer, primary_key=True)
#     code = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False)
#
#     def __init__(self, code=None, email=None):
#         self.code = code
#         self.email = email

