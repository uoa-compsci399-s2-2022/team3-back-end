from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, CheckConstraint, Enum, Table, Float
from MTMS.Models import Base
from MTMS.Utils.utils import dateTimeFormat
from MTMS.Utils.enums import StudentDegreeEnum, ApplicationStatus, ApplicationType
from MTMS.Models.courses import Term


class Application(Base):
    __tablename__ = 'application'
    ApplicationID = Column(Integer, primary_key=True)
    createdDateTime = Column(DateTime)
    submittedDateTime = Column(DateTime)
    studentID = Column(ForeignKey("users.id"))
    term = Column(ForeignKey("term.termID"))
    status = Column(Enum(ApplicationStatus))
    isResultPublished = Column(Boolean, default=False)
    resultMesg = Column(String(1024))
    type = Column(Enum(ApplicationType))

    Term = relationship("Term", back_populates="Applications")
    Users = relationship("Users", back_populates="Application")
    Courses = relationship("CourseApplication", back_populates="Application")
    SavedProfile = relationship("SavedProfile", back_populates="Application", uselist=False)
    course_users = relationship("CourseUser", back_populates="Application")



    def serialize(self):
        return {
            "applicationID": self.ApplicationID,
            "createdDateTime": dateTimeFormat(self.createdDateTime),
            "submittedDateTime": dateTimeFormat(self.submittedDateTime),
            "term": self.Term.termName,
            "termID": self.Term.termID,
            "status": self.status.name,
            "userID": self.Users.id,
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
    courseCoordinatorEndorsed = Column(Boolean, default=False)

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
            "preference": self.preference,
            "courseCoordinatorEndorsed": self.courseCoordinatorEndorsed
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
    gpa = Column(Float)

    Application = relationship('Application', back_populates='SavedProfile')

    def __setattr__(self, key, value):
        if key == 'studentDegree':
            if value in ["Undergraduate", "Postgraduate"]:
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
            'savedTime': dateTimeFormat(self.savedTime),
            'gpa': self.gpa,
        }
