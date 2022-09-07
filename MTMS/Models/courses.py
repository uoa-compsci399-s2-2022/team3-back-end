from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table
from sqlalchemy.orm import relationship
from MTMS.Models import Base




class RoleInCourse(Base):
    __tablename__ = 'RoleInCourse'
    roleID = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)

    course_users = relationship('CourseUser', back_populates='role_id')


    def __init__(self, roleID=None, Name=None, course_users=[]):
        self.roleID = roleID
        self.Name = Name
        self.course_users = course_users

    def __repr__(self):
        return '{}'.format(self.Name)

class Course(Base):

    __tablename__ = 'Course'
    courseID = Column(Integer, primary_key=True)
    courseNum = Column(String, unique=False, nullable=False)  # Eg CS399 in term1, CS399 in term2. can not be unique
    courseName = Column(String, nullable=False)  # Eg software engineering

    termID = Column(Integer, ForeignKey('Term.termID', ondelete='CASCADE'))
    term = relationship('Term', back_populates='courses', passive_deletes=True)  # 级联删除 https://docs.sqlalchemy.org/en/13/orm/cascades.html

    totalAvailableHours = Column(Float)         # how many hours does the student wants to spend.
    estimatedNumofStudents = Column(Integer)
    currentlyNumofStudents = Column(Integer)
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
    applications = relationship('CourseApplication', back_populates='course_application')

    # CourseUser
    course_users = relationship('CourseUser', back_populates='course_id')

    def __init__(self, courseID=None, courseNum=None, courseName=None, termID=None, totalAvailableHours=None,
                 estimatedNumofStudents=None, currentlyNumofStudents=None, needTutors=None,
                 needMarkers=None, numOfAssignments=None, numOfLabsPerWeek=None,
                 numOfTutorialsPerWeek=None, tutorResponsibility=None, markerResponsibility=None,
                 canPreAssign=None, applications=[], course_users=[], deadLine=None
                 ):
        self.courseID = courseID
        self.courseNum = courseNum
        self.courseName = courseName
        self.termID = termID
        self.totalAvailableHours = totalAvailableHours
        self.estimatedNumofStudents = estimatedNumofStudents
        self.currentlyNumofStudents = currentlyNumofStudents
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
            'courseNum': self.courseNum,
            'termName': self.term.termName,
            'termID': self.term.termID,
            'courseName': self.courseName,
            'totalAvailableHours': self.totalAvailableHours,
            'estimatedNumofStudents': self.estimatedNumofStudents,
            'currentlyNumofStudents': self.currentlyNumofStudents,
            'needTutors': self.needTutors,
            'needMarkers': self.needMarkers,
            'numOfAssignments': self.numOfAssignments,
            'numOfLabsPerWeek': self.numOfLabsPerWeek,
            'numOfTutorialsPerWeek': self.numOfTutorialsPerWeek,
            'tutorResponsibility': self.tutorResponsibility,
            'markerResponsibility': self.markerResponsibility,
            'canPerAssign': self.canPerAssign,
            'deadLine': self.deadLine.isoformat()
        }



    def __repr__(self):
        return "courseNum: {} courseName: {} termID: {}".format(self.courseNum, self.courseName, self.termID)



class Term(Base):
    __tablename__ = 'Term'
    termID = Column(Integer, primary_key=True)
    termName = Column(String, unique=True)
    termStartDate = Column(Date) # 后续自己设置时间
    termEndDate = Column(Date)  # yyyy-mm-dd -> 2021-01-01

    courses = relationship('Course', back_populates='term')

    def __init__(self, termID=None, termName=None, termStartDate=None, termEndDate=None, courses=[]):
        self.termID = termID
        self.termName = termName
        self.termStartDate = termStartDate
        self.termEndDate = termEndDate

        self.courses = courses



    def __repr__(self):
        return 'term name: {}. start date: {}. End date : {}'.format(
            self.termName, self.termStartDate, self.termEndDate
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
    course_id = relationship('Course', back_populates='course_users')
    role_id = relationship('RoleInCourse', back_populates='course_users')
    user_id = relationship('Users', back_populates='course_users')



class CourseApplication(Base):
    __tablename__ = 'CourseApplication'
    applicationID = Column(Integer, primary_key=True)  # 后期改成foreignkey
    courseID = Column(Integer, ForeignKey('Course.courseID'))
    course_application = relationship('Course', back_populates='applications')

    hasLearned = Column(Boolean)
    grade = Column(String)

    explanation = Column(String) # explanation of why the student wants to be a maker for this course
    preExperience = Column(String)
    result = Column(String) # result of the application

    def __init__(self, applicationID=None, courseID=None, hasLearned=None, grade=None, explanation=None, preExperience=None, result=None):
        #self.applicationID = applicationID
        self.courseID = courseID
        self.hasLearned = hasLearned
        self.grade = grade
        self.explanation = explanation
        self.preExperience = preExperience
        self.result = result

    def __repr__(self):
        pass

