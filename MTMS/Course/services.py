from MTMS import db_session
from MTMS.Models.courses import CourseUser
from MTMS.Models.users import Users
from MTMS.Models.courses import Course, Term, RoleInCourse
from MTMS.Utils.utils import response_for_services


def add_course(course: Course):
    if exist_course_in_term(courseNum=course.courseNum, termID=course.termID):
        return response_for_services(False, 'INFO:  Course existed,  {} with termID {}'.format(course.courseNum, course.termID))
    elif  not_exist_termID(course.termID):
        return response_for_services(False, 'INFO:  TermID not existed,  {} with termID {}'.format(course.courseNum, course.termID))
    else:
        db_session.add(course)
        db_session.commit()
        return response_for_services(True, "INFO:  append {} with termID {} successfully".format(course.courseNum, course.termID))

def not_exist_termID(termID):
    if db_session.query(Term).filter(Term.termID == termID).all() == []:
        return True
    return False

def exist_course_in_term(courseNum, termID) -> bool:
    if db_session.query(Course).filter(Course.courseNum == courseNum, Course.termID == termID).all() == []:
        return False
    return True

def add_term(term : Term):
    db_session.add(term)
    db_session.commit()
    return response_for_services(True, "INFO:  append {} successfully".format(term.termName))

def get_Allcourses():
    courses = db_session.query(Course).outerjoin(Term, Course.termID == Term.termID).all()
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize())
    return coourse_list

def delete_Term(termName, termStartDate, termEndDate):
    term = db_session.query(Term).filter(
        Term.termName == termName, Term.termStartDate == termStartDate, Term.termEndDate == termEndDate
    )
    if term.first() != None:
        term.delete()
        db_session.commit()
        return response_for_services(True, "INFO:  delete {} in started at {} ended at {} successfully".format(
            termName, termStartDate, termEndDate)
                                     )
    else:
        return response_for_services(False, "INFO:   {} in started at {} ended at {} does not existed".format(
            termName, termStartDate, termEndDate)
                                     )

def modify_course_info(info : dict):
    '''
        required parameter:
            :param courseNum
            :param termID

        not required, update parameter:
            courseName
            totalAvailableHours
            estimatedNumofStudents
            currentlyNumofStudents
            needTutors
            needMarkers
            numOfAssignments
            numOfLabsPerWeek
            numOfTutorialsPerWeek
            tutorResponsibility
            markerResponsibility
            canPerAssign

        eg input {'courseNum': 'cs123', 'termID': 74, 'courseName': 'software Eng', 'totalAvailableHours': 5.1}
        update courseName', totalAvailableHours
    '''
    if exist_course_in_term(courseNum=info['courseNum'], termID=info['termID']):
        course = db_session.query(Course).filter(
            Course.courseNum == info['courseNum'], Course.termID == info['termID']
        )
        for key, value in info.items():
            course.update(
                {key:value}
            )
        db_session.commit()
        return response_for_services(True, "INFO:  update {} with termID {} successfully".format(info['courseNum'], info['termID']))
    else:
        return response_for_services(False, "INFO:   {} with termID {} does not existed".format(info['courseNum'], info['termID']))



def delete_Course(courseNum, termID):
    if exist_course_in_term(courseNum=courseNum, termID=termID):
        course = db_session.query(Course).filter(
            Course.courseNum == courseNum, Course.termID == termID
        )
        course.delete()
        db_session.commit()
        return response_for_services(True, "INFO:  delete {} with termID {} successfully".format(courseNum, termID))
    else:
        return response_for_services(False, "INFO:   {} with termID {} does not existed".format(courseNum, termID))



def get_Allterms():
    terms = db_session.query(Term).all()
    d = {}
    for i in range(len(terms)):
        d[str(i)] = {
            'termName' : terms[i].termName,
            'termStartDate' : terms[i].termStartDate.strftime('%Y-%m-%d'),
            'termEndDate' : terms[i].termEndDate.strftime('%Y-%m-%d'),
        }
    #print(courses)
    return response_for_services(True, d)

def modify_Term(termID, modify_info):
    if not_exist_termID(termID):
        return response_for_services(False, "INFO:   {} does not existed".format(termID))
    else:
        term = db_session.query(Term).filter(
            Term.termID == termID
        )
        for key, value in modify_info.items():
            term.update(
                {key:value}
            )
        db_session.commit()
        return response_for_services(True, "INFO:  update {} successfully".format(termID))


def add_CourseUser(courseID,userID, *args):
    try:
        course = db_session.query(Course).filter(Course.courseID == courseID).first()
        user = db_session.query(Users).filter(Users.id == userID).first()
        if course == None:
            return response_for_services(False, "INFO:   '{}' does not existed".format(courseID))
        elif user == None:
            return response_for_services(False, "INFO:   '{}' does not existed".format(userID))
        else:
            course_user = CourseUser()
            course_user.courseID = courseID
            course_user.userID = userID
            if args == ():
                db_session.add(course_user)
                db_session.commit()
                return response_for_services(True, "INFO:  append '{}' to '{}' successfully".format(userID, courseID))
            else:
                role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == args[0]).first()
                if role == None:
                    return response_for_services(False, "INFO:   '{}' does not existed".format(args[0]))
                course_user.roleID = role.roleID
                db_session.add(course_user)
                db_session.commit()
                return response_for_services(True, "INFO:  append {} {} to {} successfully".format(userID, args[0] ,courseID))
    except:
        return response_for_services(False, "INFO:   '{}' and '{}' already existed".format(userID, courseID))

def modify_CourseUser(arg : dict ):

    course_user = db_session.query(CourseUser).filter(arg['courseID'] == CourseUser.courseID, arg['userID'] == CourseUser.userID)
    if course_user.first() == None:
        return response_for_services(False, "INFO:   '{}' and '{}' does not existed".format(arg['userID'], arg['courseID']))
    for key, value in arg.items():
        course_user.update(
            {key:value}
        )
    db_session.commit()
    return response_for_services(True, "INFO:  update  {} {} successfully".format(arg['userID'], arg['courseID']))

def get_CourseUser(courseID, userID):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID, CourseUser.userID == userID).first()

    if course_user == None:
        return response_for_services(False, "INFO:   '{}' and '{}' does not existed".format(userID, courseID))
    else:
        return response_for_services(True, {'courseID': course_user.courseID, 'userID': course_user.userID, 'roleID': course_user.roleID})

def delete_CourseUser(courseID, userID):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID, CourseUser.userID == userID)
    if course_user.first() == None:
        return response_for_services(False, "INFO:   '{}' and '{}' does not existed".format(userID, courseID))
    else:
        course_user.delete()
        db_session.commit()
        return response_for_services(True, "INFO:  delete  {} {} successfully".format(userID, courseID))


def add_RoleInCourse(Name):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == Name).first()
    if role == None:
        role = RoleInCourse()
        role.Name = Name
        db_session.add(role)
        db_session.commit()
        return response_for_services(True, "INFO:  add '{}' successfully".format(Name))
    else:
        return response_for_services(False, "INFO:   '{}' already existed".format(Name))

def get_RoleInCourse(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID).first()
    if role == None:
        return response_for_services(False, "INFO:   '{}' does not existed".format(roleID))
    else:
        return response_for_services(True, {'roleID': role.roleID, 'Name': role.Name})

def delete_RoleInCourse(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID)
    if role.first() == None:
        return response_for_services(False, "INFO:   '{}' does not existed".format(roleID))
    else:
        role.delete()
        db_session.commit()
        return response_for_services(True, "INFO:  delete '{}' successfully".format(roleID))

def modify_RoleInCourse(args : dict):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == args['roleID'])
    if role.first() == None:
        return response_for_services(False, "INFO:   '{}' does not existed".format(args['roleID']))
    else:
        for key, value in args.items():
            role.update(
                {key:value}
            )
        db_session.commit()
        return response_for_services(True, "INFO:  update '{}' successfully".format(args['roleID']))
