from MTMS import db_session
from MTMS.Models.courses import CourseUser
from MTMS.Models.users import Users
from MTMS.Models.courses import Course, Term, RoleInCourse
from MTMS.Utils.utils import response_for_services


# Course
def add_course(args):
    if not_exist_termID(args['termID']):
        return (False, 'TermID:{} not existed'.format(args['termID']))
    if exist_course_in_term(courseNum=args['courseNum'], termID=args['termID']):
        return (False, 'Course existed,  {} with termID:{}'.format(args['courseNum'], args['termID']))
    new_course = Course(courseNum=args['courseNum'],
                        courseName=args['courseName'],
                        termID=args['termID'])
    for key, value in args.items():
        if key not in ['courseNum', 'courseName', 'termID']:
            temp_value = value
            exec(f"new_course.{key} = temp_value")

    if 'deadline' not in args:
        new_course.deadline = db_session.query(Term.defaultDeadLine).filter(Term.termID == args['termID']).one_or_none()
    db_session.add(new_course)
    db_session.commit()
    return (True, "append {} with termID:{} successfully".format(new_course.courseNum, new_course.termID))


def exist_course_in_term(courseNum, termID) -> bool:
    if db_session.query(Course).filter(Course.courseNum == courseNum, Course.termID == termID).one_or_none() is None:
        return False
    return True


def get_course_by_id(courseID):
    return db_session.query(Course).filter(Course.courseID == courseID).one_or_none()


def get_Allcourses():
    courses = db_session.query(Course).outerjoin(Term, Course.termID == Term.termID).all()
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize())
    return coourse_list


def get_course_by_term(termID):
    courses = db_session.query(Course).outerjoin(Term, Course.termID == Term.termID).filter(Term.termID == termID).all()
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize())
    return coourse_list


def modify_course_info(info: dict, courseID):
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
    try:
        course = get_course_by_id(courseID)
        if 'termID' in info and not_exist_termID(info['termID']):
            return (False, f"termID:{info['termID']} does not existed")
        if course is not None:
            course_filter = db_session.query(Course).filter(
                Course.courseID == courseID
            )
            for key, value in info.items():
                course_filter.update(
                    {key: value}
                )
            db_session.commit()
            db_session.refresh(course)
            return (True, f"update courseID:{courseID}({course.courseNum} - {course.term.termName}) successfully")
        else:
            return (False, f"courseID:{courseID} does not existed")
    except:
        return (False, "Unexpected Error")


def delete_Course(courseID):
    course = get_course_by_id(courseID)

    if course:
        courseNum = course.courseNum
        termName = course.term.termName
        db_session.delete(course)
        db_session.commit()
        return (True, f"delete courseID:{courseID}({courseNum} - {termName}) successfully", 200)
    else:
        return (False, f"courseID:{courseID} does not existed", 404)


# Term
def add_term(term: Term):
    db_session.add(term)
    db_session.commit()
    return (True, "append {} successfully".format(term.termName), 200)


def not_exist_termID(termID):
    if db_session.query(Term).filter(Term.termID == termID).one_or_none() is None:
        return True
    return False


def exist_termName(termName):
    if db_session.query(Term).filter(Term.termName == termName).one_or_none() is None:
        return False
    return True


def get_term_by_id(termID):
    return db_session.query(Term).filter(Term.termID == termID).one_or_none()


def delete_Term(termID):
    term = get_term_by_id(termID)
    if term:
        db_session.delete(term)
        db_session.commit()
        return (True, f"delete termID:{termID} successfully", 200)
    else:
        return (False, f"termID:{termID} does not existed", 404)


def get_Allterms():
    terms = db_session.query(Term).all()
    terms_list = []
    for i in range(len(terms)):
        terms_list.append(terms[i].serialize())
    return terms_list

def get_available_term():
    # terms = db_session.query(Term).filter(Term.isAvailable == True).all()

    terms = db_session.query(Term).all()
    terms_list = []
    for i in range(len(terms)):
        terms_list.append(terms[i].serialize())
    return terms_list


def modify_Term(termID, modify_info):
    term = get_term_by_id(termID)
    if not term:
        return (False, "{} does not existed".format(termID), 404)
    else:
        term = db_session.query(Term).filter(
            Term.termID == termID
        )
        for key, value in modify_info.items():
            term.update(
                {key: value}
            )
        db_session.commit()
        return (True, "update {} successfully".format(termID), 200)


# Enrolment (That is, the correspondence between each course and the user)
def add_CourseUser(courseID, userID, roleName):
    try:
        # existence checking
        course = db_session.query(Course).filter(Course.courseID == courseID).first()
        user = db_session.query(Users).filter(Users.id == userID).first()
        if course is None and user is None:
            return (False, f"course:{courseID} and user:{userID} does not existed", 404)
        elif user is None:
            return (False, "user:{} does not existed".format(userID), 404)
        elif course is None:
            return (False, "course:'{}' does not existed".format(courseID), 404)
        courseUser = db_session.query(CourseUser).filter(CourseUser.courseID == courseID,
                                                         CourseUser.userID == userID).one_or_none()
        if courseUser:
            return (False, f"{userID} has already enrolled in {course.courseNum} - {course.term.termName}", 400)
        role = get_RoleInCourse_by_name(roleName)
        if role is None:
            return (False, f"role '{roleName}' does not existed", 404)

        # create new CourseUser
        course_user = CourseUser()
        course_user.courseID = courseID
        course_user.userID = userID
        course_user.roleID = role.roleID
        db_session.add(course_user)
        db_session.commit()
        return (True, "Successful Enrolment", 200)
    except:
        return (False, "Unexpected Error", 400)


def modify_CourseUser(arg: dict):
    course_user: CourseUser = db_session.query(CourseUser).filter(arg['courseID'] == CourseUser.courseID,
                                                                  arg['userID'] == CourseUser.userID).one_or_none()
    if not course_user:
        return (False,
                f"{arg['userID']} has not enrolled in courseID:{arg['courseID']}", 404)

    role = get_RoleInCourse_by_name(arg['role'])
    if role is None:
        return (False, f"role '{arg['role']}' does not existed", 404)
    course_user.roleID = role.roleID
    db_session.commit()
    return (True, "update role successfully", 200)


def get_enrolment_role(courseID, userID):
    course_user: CourseUser = db_session.query(CourseUser).filter(CourseUser.courseID == courseID,
                                                                  CourseUser.userID == userID).one_or_none()
    if course_user is None:
        return None
    else:
        role: RoleInCourse = get_RoleInCourse_by_id(course_user.roleID)
        if role is None:
            return None
        else:
            return role.Name


def get_user_enrolment(userID):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == Course.courseID).filter(
        CourseUser.userID == userID).all()
    result = []
    for cu in course_user:
        result.append({
            "userID": userID,
            "courseID": cu.courseID,
            "role": cu.role.Name,
            "courseNum": cu.course.courseName,
            "termName": cu.course.term.termName,
            "termID": cu.course.termID,
            "courseName": cu.course.courseName,
        })
    return result


def get_user_enrolment_in_term(userID, termID):
    course_user = db_session.query(CourseUser).join(Course).filter(
        Course.termID == termID, CourseUser.userID == userID).all()
    return course_user


def get_course_user(courseID):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID).all()
    result = []
    for i in course_user:
        user_dict = i.user.profile_serialize()
        user_dict.update({"roleInCourse": i.role.Name})
        result.append(user_dict)
    return result

def get_course_user_by_roleInCourse(courseID, roleInCourseList: list):
    course_user = db_session.query(CourseUser).join(RoleInCourse).filter(CourseUser.courseID == courseID,
                                                                         RoleInCourse.Name.in_(roleInCourseList)).all()
    return course_user



def delete_CourseUser(courseID, userID):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID, CourseUser.userID == userID)
    if course_user.first() == None:
        return response_for_services(False, "INFO:   '{}' and '{}' does not existed".format(userID, courseID))
    else:
        course_user.delete()
        db_session.commit()
        return response_for_services(True, "INFO:  delete  {} {} successfully".format(userID, courseID))


def get_RoleInCourse_by_name(roleName):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == roleName).one_or_none()
    return role


def get_RoleInCourse_by_id(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID).one_or_none()
    return role

def get_user_metaData(user_id):
    # 无需登录
    metaData = {}
    userdata = db_session.query(Users).filter(Users.id == user_id).first()
    metaData['id'] = userdata.id
    metaData['name'] = userdata.name
    metaData['email'] = userdata.email
    metaData['otherContracts'] = userdata.otherContracts
    # metaData['academicRecord'] = userdata.academicRecord
    return metaData

def get_termName_termID(termID):
    term = db_session.query(Term).filter(Term.termID == termID).first()
    return term.termName

def get_CourseBy_userID(userID, termID):
    course_user = db_session.query(CourseUser).filter(CourseUser.userID == userID).all()

    result = []
    for i in course_user:
        if i.course.termID == termID:
            result.append(i.course.serialize())
    return result