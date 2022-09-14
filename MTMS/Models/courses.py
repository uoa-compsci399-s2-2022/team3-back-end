from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table
from sqlalchemy.orm import relationship
from MTMS.Models import Base
from MTMS.Utils.utils import dateTimeFormat



class RoleInCourse(Base):
    __tablename__ = 'RoleInCourse'
    roleID = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    course_users = relationship('CourseUser', back_populates='role')


    def __init__(self, roleID=None, Name=None, course_users=[]):
        self.roleID = roleID
        self.Name = Name
        self.course_users = course_users

    def __repr__(self):
        return '{}'.format(self.Name)

    def serialize(self):
        return {
            'roleID': self.roleID,
            'Name': self.Name
        }


class Course(Base):
    __tablename__ = 'Course'
    courseID = Column(Integer, primary_key=True)
    courseNum = Column(String, unique=False, nullable=False)  # Eg CS399 in term1, CS399 in term2. can not be unique
    courseName = Column(String, nullable=False)  # Eg software engineering

    termID = Column(Integer, ForeignKey('Term.termID', ondelete='CASCADE'))
    term = relationship('Term', back_populates='courses', passive_deletes=True)  # 级联删除 https://docs.sqlalchemy.org/en/13/orm/cascades.html

    totalAvailableHours = Column(Float)         # how many hours does the student wants to spend.
    estimatedNumOfStudents = Column(Integer)
    currentlyNumOfStudents = Column(Integer)
    needTutors = Column(Boolean)
    needMarkers = Column(Boolean)
    numOfAssignments = Column(Integer)
    numOfLabsPerWeek = Column(Integer)
    numOfTutorialsPerWeek = Column(Integer)
    tutorResponsibility = Column(String)       # short brief description of the responsibility of the tutor for the course
    markerResponsibility = Column(String)
    canPreAssign = Column(Boolean)
    deadLine = Column(DateTime)

    # application
    Applications = relationship('CourseApplication', back_populates='Course')

    # CourseUser
    course_users = relationship('CourseUser', back_populates='course')

    def __init__(self, courseNum, courseName, termID, totalAvailableHours=None,
                 estimatedNumOfStudents=None, currentlyNumOfStudents=None, needTutors=None,
                 needMarkers=None, numOfAssignments=None, numOfLabsPerWeek=None,
                 numOfTutorialsPerWeek=None, tutorResponsibility=None, markerResponsibility=None,
                 canPreAssign=None, applications=[], course_users=[], deadLine=None
                 ):
        self.courseNum = courseNum
        self.courseName = courseName
        self.termID = termID
        self.totalAvailableHours = totalAvailableHours
        self.currentlyNumOfStudents = estimatedNumOfStudents
        self.currentlyNumOfStudents = currentlyNumOfStudents
        self.needTutors = needTutors
        self.needMarkers = needMarkers
        self.numOfAssignments = numOfAssignments
        self.numOfLabsPerWeek = numOfLabsPerWeek
        self.numOfTutorialsPerWeek = numOfTutorialsPerWeek
        self.tutorResponsibility = tutorResponsibility
        self.markerResponsibility = markerResponsibility
        self.canPreAssign = canPreAssign
        self.applications = applications
        self.course_users = course_users
        self.deadLine = deadLine


    def serialize(self):
        return {
            'courseID': self.courseID,
            'courseNum': self.courseNum,
            'termName': self.term.termName,
            'termID': self.term.termID,
            'courseName': self.courseName,
            'totalAvailableHours': self.totalAvailableHours,
            'estimatedNumOfStudents': self.estimatedNumOfStudents,
            'currentlyNumOfStudents': self.currentlyNumOfStudents,
            'needTutors': self.needTutors,
            'needMarkers': self.needMarkers,
            'numOfAssignments': self.numOfAssignments,
            'numOfLabsPerWeek': self.numOfLabsPerWeek,
            'numOfTutorialsPerWeek': self.numOfTutorialsPerWeek,
            'tutorResponsibility': self.tutorResponsibility,
            'markerResponsibility': self.markerResponsibility,
            'canPerAssign': self.canPreAssign,
            'deadLine': dateTimeFormat(self.deadLine)
        }

    def __repr__(self):
        return "courseNum: {} courseName: {} termID: {}".format(self.courseNum, self.courseName, self.termID)



class Term(Base):
    __tablename__ = 'Term'
    termID = Column(Integer, primary_key=True)
    termName = Column(String, unique=True)
    startDate = Column(Date) # 后续自己设置时间
    endDate = Column(Date)  # yyyy-mm-dd -> 2021-01-01
    isAvailable = Column(Boolean)
    courses = relationship('Course', back_populates='term')

    def __init__(self, termName, startDate=None, endDate=None, courses=[], isAvailable=True):
        self.termName = termName
        self.startDate = startDate
        self.endDate = endDate
        self.courses = courses
        self.isAvailable = isAvailable

    def serialize(self):
        return {
            'termID': self.termID,
            'termName': self.termName,
            'startDate': dateTimeFormat(self.startDate),
            'endDate': dateTimeFormat(self.endDate),
        }

    def __repr__(self):
        return 'term name: {}. start date: {}. End date : {}'.format(
            self.termName, self.startDate, self.endDate
        )




# This page shows how to create a many to many relationship between two tables.
# Also shows an association relationship table (link 3 more table together ).
# reference  https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object



# an association table for the role, course and user  many to many relationship
class CourseUser(Base):
    __tablename__ = 'CourseUser'
    courseID = Column(Integer, ForeignKey('Course.courseID'), primary_key=True)
    userID = Column(Integer, ForeignKey('Users.id'), primary_key=True)
    roleID = Column(Integer, ForeignKey('RoleInCourse.roleID'), primary_key=False)

    # approved = Column(Boolean, default=False)
    course = relationship('Course', back_populates='course_users')
    role = relationship('RoleInCourse', back_populates='course_users')
    user = relationship('Users', back_populates='course_users')



