from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from MTMS.Models import Base
from MTMS.Utils.utils import dateTimeFormat
from typing import List


class RoleInCourse(Base):
    __tablename__ = 'role_in_course'
    roleID = Column(Integer, primary_key=True)
    Name = Column(String(255), unique=True)

    course_users = relationship('CourseUser', back_populates='role', cascade='all, delete-orphan')

    def __init__(self, roleID=None, Name=None):
        self.roleID = roleID
        self.Name = Name

    def __repr__(self):
        return '{}'.format(self.Name)

    def serialize(self):
        return {
            'roleID': self.roleID,
            'Name': self.Name
        }


class Payday(Base):
    __tablename__ = 'payday'
    paydayID = Column(Integer, primary_key=True)
    termID = Column(ForeignKey('term.termID'))
    payday = Column(DateTime)

    Term = relationship('Term', back_populates='Paydays')
    WorkingHours = relationship('WorkingHours', back_populates='Payday', cascade='all, delete-orphan',
                                foreign_keys='WorkingHours.paydayID')

    def serialize(self):
        return {
            'paydayID': self.paydayID,
            'termID': self.termID,
            'payday': dateTimeFormat(self.payday)
        }


class Course(Base):
    __tablename__ = 'course'
    courseID = Column(Integer, primary_key=True, autoincrement=True)
    courseNum = Column(String(255), unique=False,
                       nullable=False)  # Eg CS399 in term1, CS399 in term2. can not be unique
    courseName = Column(String(255), nullable=False)  # Eg software engineering

    termID = Column(Integer, ForeignKey('term.termID'))
    term = relationship('Term', back_populates='courses')

    totalAvailableHours = Column(Float)  # how many hours does the student wants to spend.
    estimatedNumOfStudents = Column(Integer)
    currentlyNumOfStudents = Column(Integer)
    needTutors = Column(Boolean)
    needMarkers = Column(Boolean)
    numOfAssignments = Column(Integer)
    numOfLabsPerWeek = Column(Integer)
    numOfTutorialsPerWeek = Column(Integer)
    tutorResponsibility = Column(
        String(255))  # short brief description of the responsibility of the tutor for the course
    markerResponsibility = Column(String(255))
    canPreAssign = Column(Boolean)
    markerDeadLine = Column(DateTime)
    tutorDeadLine = Column(DateTime)
    prerequisite = Column(String)

    # application
    Applications = relationship('CourseApplication', back_populates='Course')

    # CourseUser
    course_users = relationship('CourseUser', back_populates='course', cascade="all, delete-orphan")

    def getCurrentPublishedAvailableHours(self):
        return count_current_available_hours(self.totalAvailableHours, self.courseID, True)

    def __init__(self, courseNum, courseName, termID, totalAvailableHours=0.0,
                 estimatedNumOfStudents=None, currentlyNumOfStudents=None, needTutors=None,
                 needMarkers=None, numOfAssignments=None, numOfLabsPerWeek=None,
                 numOfTutorialsPerWeek=None, tutorResponsibility=None, markerResponsibility=None,
                 canPreAssign=None, applications=[], course_users=[], markerDeadLine=None, tutorDeadLine=None,
                 prerequisite=None
                 ):
        self.courseNum = courseNum
        self.courseName = courseName
        self.termID = termID
        self.totalAvailableHours = totalAvailableHours
        self.estimatedNumOfStudents = estimatedNumOfStudents
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
        self.markerDeadLine = markerDeadLine
        self.tutorDeadLine = tutorDeadLine
        self.prerequisite = prerequisite

    def serialize(self):
        return {
            'courseID': self.courseID,
            'courseNum': self.courseNum,
            'termName': self.term.termName,
            'termID': self.term.termID,
            'courseName': self.courseName,
            'totalAvailableHours': self.totalAvailableHours,
            'currentAvailableHours': count_current_available_hours(self.totalAvailableHours, self.courseID),
            'currentPublishedAvailableHours': count_current_available_hours(self.totalAvailableHours, self.courseID,
                                                                            True),
            'estimatedNumOfStudents': self.estimatedNumOfStudents,
            'currentlyNumOfStudents': self.currentlyNumOfStudents,
            'needTutors': self.needTutors,
            'needMarkers': self.needMarkers,
            'numOfAssignments': self.numOfAssignments,
            'numOfLabsPerWeek': self.numOfLabsPerWeek,
            'numOfTutorialsPerWeek': self.numOfTutorialsPerWeek,
            'tutorResponsibility': self.tutorResponsibility,
            'markerResponsibility': self.markerResponsibility,
            'canPreAssign': self.canPreAssign,
            'markerDeadLine': dateTimeFormat(self.markerDeadLine),
            'tutorDeadLine': dateTimeFormat(self.tutorDeadLine),
            'prerequisite': self.prerequisite
        }

    def serialize_simple(self):
        return {
            'courseID': self.courseID,
            'courseNum': self.courseNum,
            'termName': self.term.termName,
            'termID': self.term.termID,
            'courseName': self.courseName,
            'needTutors': self.needTutors,
            'needMarkers': self.needMarkers,
            'prerequisite': self.prerequisite
        }

    def __repr__(self):
        return "courseNum: {} courseName: {} termID: {}".format(self.courseNum, self.courseName, self.termID)


class Term(Base):
    __tablename__ = 'term'
    termID = Column(Integer, primary_key=True)
    termName = Column(String(255), unique=True)
    startDate = Column(DateTime)  # 后续自己设置时间
    endDate = Column(DateTime)  # yyyy-mm-dd -> 2021-01-01
    isAvailable = Column(Boolean)
    defaultMarkerDeadLine = Column(DateTime)
    defaultTutorDeadLine = Column(DateTime)

    courses = relationship('Course', back_populates='term', cascade="all, delete-orphan")
    Applications = relationship('Application', back_populates='Term')

    # Payday
    Paydays: List[Payday] = relationship('Payday', back_populates='Term', cascade="all, delete-orphan")

    def __init__(self, termName, startDate=None, endDate=None, courses=[], isAvailable=True, defaultMarkerDeadLine=None,
                 defaultTutorDeadLine=None):
        self.termName = termName
        self.startDate = startDate
        self.endDate = endDate
        self.courses = courses
        self.isAvailable = isAvailable
        self.defaultMarkerDeadLine = defaultMarkerDeadLine
        self.defaultTutorDeadLine = defaultTutorDeadLine

    def serialize(self):
        if self.Paydays is None:
            paydays = None
        else:
            paydays = [i.serialize() for i in self.Paydays]
        return {
            'termID': self.termID,
            'termName': self.termName,
            'startDate': dateTimeFormat(self.startDate),
            'endDate': dateTimeFormat(self.endDate),
            'isAvailable': self.isAvailable,
            'defaultMarkerDeadLine': dateTimeFormat(self.defaultMarkerDeadLine),
            'defaultTutorDeadLine': dateTimeFormat(self.defaultTutorDeadLine),
            'paydays': paydays
        }

    def __repr__(self):
        return 'term name: {}. start date: {}. End date : {}'.format(
            self.termName, self.startDate, self.endDate
        )


class WorkingHours(Base):
    __tablename__ = 'working_hours'
    courseID = Column(Integer, primary_key=True)
    userID = Column(String(255), primary_key=True)
    roleID = Column(Integer, primary_key=True)
    paydayID = Column(ForeignKey('payday.paydayID'), primary_key=True)
    actualHours = Column(Float)
    isApproved = Column(Boolean, default=False)

    CourseUser = relationship('CourseUser', back_populates='WorkingHours')
    Payday = relationship('Payday', back_populates='WorkingHours')

    __table_args__ = (
        ForeignKeyConstraint(
            (courseID, userID, roleID),
            ['course_user.courseID', 'course_user.userID', 'course_user.roleID'],
        ),
    )

    def serialize(self):
        return {
            'courseID': self.courseID,
            'userID': self.userID,
            'roleID': self.roleID,
            'paydayID': self.paydayID,
            'payday': dateTimeFormat(self.Payday.payday) if self.Payday is not None else None,
            'actualHours': self.actualHours,
            'isApproved': self.isApproved
        }


# This page shows how to create a many to many relationship between two tables.
# Also shows an association relationship table (link 3 more table together ).
# reference  https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object

# an association table for the role, course and user  many to many relationship
class CourseUser(Base):
    __tablename__ = 'course_user'
    courseID = Column(Integer, ForeignKey('course.courseID'), primary_key=True)
    userID = Column(String(255), ForeignKey('users.id'), primary_key=True)
    roleID = Column(Integer, ForeignKey('role_in_course.roleID'), primary_key=True)
    ApplicationID = Column(ForeignKey('application.ApplicationID'), nullable=True)
    estimatedHours = Column(Float)
    isPublished = Column(Boolean, default=False)

    course = relationship('Course', back_populates='course_users')
    role = relationship('RoleInCourse', back_populates='course_users')
    user = relationship('Users', back_populates='course_users')
    Application = relationship('Application', back_populates='course_users')
    WorkingHours = relationship('WorkingHours', back_populates='CourseUser', cascade='all, delete-orphan')

    def serialize(self):
        return {
            'courseID': self.courseID,
            'userID': self.userID,
            'roleID': self.roleID,
            'roleName': self.role.Name,
            'courseName': self.course.courseName,
            'courseNum': self.course.courseNum,
            'estimatedHours': self.estimatedHours,
            'isPublished': self.isPublished
        }

    def serialize_with_course_information(self):
        return {
            'courseID': self.courseID,
            'userID': self.userID,
            'roleID': self.roleID,
            'roleName': self.role.Name if self.role is not None else None,
            'courseName': self.course.courseName,
            'courseNum': self.course.courseNum,
            'estimatedHours': self.estimatedHours,
            'isPublished': self.isPublished,
            'totalAvailableHours': self.course.totalAvailableHours,
            'currentAvailableHours': count_current_available_hours(self.course.totalAvailableHours, self.courseID),
            'currentPublishedAvailableHours': count_current_available_hours(self.course.totalAvailableHours,
                                                                            self.courseID, True),
        }

    def serialize_with_user_information(self):
        return {
            'courseID': self.courseID,
            'userID': self.userID,
            'roleID': self.roleID,
            'roleName': self.role.Name if self.role is not None else None,
            'name': self.user.name,
            'email': self.user.email,
        }

    def serialize_with_working_hours(self):
        result = {
            'courseID': self.courseID,
            'userID': self.userID,
            'roleID': self.roleID,
            'roleName': self.role.Name if self.role is not None else None,
            'isPublished': self.isPublished,
            'estimatedHours': self.estimatedHours,
        }

        if self.WorkingHours is not None:
            result['workingHours'] = [workingHour.serialize() for workingHour in self.WorkingHours]
        return result


def count_current_available_hours(totalAvailableHours, courseID, isPublished: bool = None):
    from MTMS import db_session
    if isPublished is None:
        currentEstimatedHours = sum(
            [i[0] for i in db_session.query(CourseUser.estimatedHours).filter(CourseUser.courseID == courseID).all() if
             i[0] is not None])
    else:
        currentEstimatedHours = sum(
            [i[0] for i in db_session.query(CourseUser.estimatedHours).filter(CourseUser.courseID == courseID,
                                                                              CourseUser.isPublished == isPublished).all()
             if i[0] is not None])
    if totalAvailableHours is None:
        currentAvailableHours = None
    else:
        currentAvailableHours = totalAvailableHours - (currentEstimatedHours if currentEstimatedHours is not None else 0)
    return currentAvailableHours
