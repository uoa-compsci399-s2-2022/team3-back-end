import datetime
from typing import List
import pandas as pd

from MTMS import db_session
from MTMS.Models.courses import CourseUser
from MTMS.Models.users import Users
from MTMS.Models.courses import Course, Term, RoleInCourse


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
    if 'markerDeadLine' not in args:
        markerDeadLine = db_session.query(Term.defaultMarkerDeadLine).filter(
            Term.termID == args['termID']).one_or_none()
        if markerDeadLine:
            new_course.markerDeadLine = markerDeadLine[0]
    if 'tutorDeadLine' not in args:
        tutorDeadLine = db_session.query(Term.defaultTutorDeadLine).filter(Term.termID == args['termID']).one_or_none()
        if tutorDeadLine:
            new_course.tutorDeadLine = tutorDeadLine[0]

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
    courses = db_session.query(Course).all()
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize())
    return coourse_list


def get_course_by_term(termID):
    courses = db_session.query(Course).filter(Course.termID == termID).all()
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize())
    return coourse_list


def get_simple_course_by_term(termID):
    courses: Course = db_session.query(Course).filter(Course.termID == termID).all()
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize_simple())
    return coourse_list


def get_simple_course_by_term_and_position(termID, position):
    if position == 'tutor':
        courses: Course = db_session.query(Course).filter(Course.termID == termID, Course.needTutors).all()
    elif position == 'marker':
        courses: Course = db_session.query(Course).filter(Course.termID == termID, Course.needMarkers).all()
    elif position == 'all':
        courses: Course = db_session.query(Course).filter(Course.termID == termID).all()
    else:
        return False, 'Invalid position', 400
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize_simple())
    return coourse_list


def get_simple_course_by_courseNum(termID, courseNum, position):
    if position == 'tutor':
        courses = db_session.query(Course).filter(Course.courseNum.like(f"%{courseNum}%"), Course.termID == termID,
                                                  Course.needTutors).all()
    elif position == 'marker':
        courses = db_session.query(Course).filter(Course.courseNum.like(f"%{courseNum}%"), Course.termID == termID,
                                                  Course.needMarkers).all()
    elif position == 'all':
        courses = db_session.query(Course).filter(Course.courseNum.like(f"%{courseNum}%"),
                                                  Course.termID == termID).all()
    else:
        return False, 'Invalid position', 400
    coourse_list = []
    for i in range(len(courses)):
        coourse_list.append(courses[i].serialize_simple())
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
def not_exist_termID(termID):
    if db_session.query(Term).filter(Term.termID == termID).one_or_none() is None:
        return True
    return False


def exist_termName(termName):
    if db_session.query(Term).filter(Term.termName == termName.strip()).one_or_none() is None:
        return False
    return True


def get_term_by_id(termID):
    return db_session.query(Term).filter(Term.termID == termID).one_or_none()


def delete_Term(termID):
    term = get_term_by_id(termID)
    if term:
        db_session.delete(term)
        db_session.commit()
        return True, f"delete termID:{termID} successfully", 200
    else:
        return False, f"termID:{termID} does not existed", 404


def get_Allterms():
    terms = db_session.query(Term).all()
    terms_list = []
    for i in range(len(terms)):
        terms_list.append(terms[i].serialize())
    return terms_list


# Enrolment (That is, the correspondence between each course and the user)
def add_CourseUser(courseID, userID, roleName, estimatedHours):
    try:
        # existence checking
        course = db_session.query(Course).filter(Course.courseID == courseID).first()
        user = db_session.query(Users).filter(Users.id == userID).first()
        if course is None and user is None:
            return False, f"course:{courseID} and user:{userID} does not existed", 404
        elif user is None:
            return False, "user:{} does not existed".format(userID), 404
        elif course is None:
            return False, "course:'{}' does not existed".format(courseID), 404
        role = get_RoleInCourse_by_name(roleName)
        if role is None:
            return False, f"role '{roleName}' does not existed", 404
        courseUser = db_session.query(CourseUser).filter(CourseUser.courseID == courseID,
                                                         CourseUser.userID == userID,
                                                         CourseUser.roleID == role.roleID).one_or_none()
        if courseUser and courseUser.isPublished:
            return False, f"{userID} has already enrolled in {course.courseNum} - {course.term.termName}", 400
        elif courseUser and not courseUser.isPublished:
            return False, f"You have approved {userID} as a {roleName} but have not published yet", 400

        # create new CourseUser
        course_user = CourseUser(
            courseID=courseID,
            userID=userID,
            roleID=role.roleID,
            isPublished=True,
            estimatedHours=estimatedHours if estimatedHours else None
        )
        db_session.add(course_user)
        db_session.commit()
        return True, "Successful Enrolment", 200
    except:
        return False, "Unexpected Error", 400


def modify_CourseUser(course, user: Users, role):
    try:
        courseUser: list[CourseUser] = db_session.query(CourseUser).filter(CourseUser.courseID == course.courseID,
                                                                           CourseUser.userID == user.id).all()
        # Delete
        for cu in courseUser:
            if cu.role.Name not in role:
                db_session.delete(cu)

        # Add
        for roleName in role:
            roleObj = get_RoleInCourse_by_name(roleName)
            if roleObj is None:
                db_session.rollback()
                return False, f"role '{roleName}' does not existed", 404
            if roleName in [cu.role.Name for cu in courseUser]:
                continue
            course_user = CourseUser(
                courseID=course.courseID,
                userID=user.id,
                roleID=roleObj.roleID,
                isPublished=True
            )
            db_session.add(course_user)
        db_session.commit()
        return True, "update role successfully", 200
    except:
        db_session.rollback()
        return False, "Unexpected Error", 400


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
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == Course.courseID,
                                                      CourseUser.isPublished == True).filter(
        CourseUser.userID == userID).all()
    result = []
    for cu in course_user:
        result.append({
            "userID": userID,
            "courseID": cu.courseID,
            "role": cu.role.Name,
            "courseNum": cu.course.courseName,
            "termName": cu.course.term.termName if cu.course.term else None,
            "termID": cu.course.termID,
            "courseName": cu.course.courseName,
        })
    return result


def get_user_enrolment_in_term(userID, termID):
    course_user = db_session.query(CourseUser).join(Course).filter(
        Course.termID == termID, CourseUser.userID == userID, CourseUser.isPublished == True).all()
    return course_user


def get_course_user_by_courseID_isPublish(courseID, isPublished):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID,
                                                      CourseUser.isPublished == isPublished).all()
    result = []
    for i in course_user:
        user_dict = i.user.profile_serialize()
        user_dict.update({"roleInCourse": i.role.Name})
        result.append(user_dict)
    return result


def get_course_user_with_public_information(courseID):
    course_user: List[CourseUser] = db_session.query(CourseUser).filter(CourseUser.courseID == courseID).all()
    result = []
    for i in course_user:
        if i.user is None:
            return False, "Enrollment Information Error", 400
        user_dict = i.user.profile_serialize()
        user_dict.update(
            {"roleInCourse": i.role.Name, "isPublished": i.isPublished, "estimatedHours": i.estimatedHours,
             "workingHours": [wh.serialize() for wh in i.WorkingHours]})
        result.append(user_dict)
    return True, result, 200


def get_course_user_by_roleInCourse(courseID, roleInCourseList: list):
    course_user = db_session.query(CourseUser).join(RoleInCourse).filter(CourseUser.courseID == courseID,
                                                                         CourseUser.isPublished == True,
                                                                         RoleInCourse.Name.in_(roleInCourseList)).all()
    return course_user


def delete_CourseUser(courseID, userID, roleName):
    course_user = db_session.query(CourseUser).join(RoleInCourse).filter(CourseUser.courseID == courseID,
                                                                         CourseUser.userID == userID,
                                                                         RoleInCourse.Name == roleName).one_or_none()
    if course_user is None:
        return False, "{} in CourseID: {}(role: {}) does not existed".format(userID, courseID, roleName), 404
    else:
        db_session.delete(course_user)
        db_session.commit()
        return True, "Delete {} in CourseID: {}(role: {}) successfully".format(userID, courseID, roleName), 200


def get_RoleInCourse_by_name(roleName):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == roleName).one_or_none()
    return role


def get_RoleInCourse_by_id(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID).one_or_none()
    return role


def get_termName_termID(termID):
    term = db_session.query(Term).filter(Term.termID == termID).first()
    return term.termName


def get_CourseBy_userID(userID, termID):
    course_user = db_session.query(CourseUser).filter(CourseUser.userID == userID, CourseUser.isPublished).all()
    result = []
    for i in course_user:
        if i.course.termID == termID:
            result.append(i.serialize())
    return result


def Load_Courses(termID, filestream):
    df = pd.read_excel(filestream)
    headers = df.columns.values.tolist()
    if 'courseNum' not in headers or 'courseName' not in headers:  # 未找到必传参数
        return False
    else:
        for i in range(len(headers) - 1, -1, -1):
            attr = headers[i]
            try:
                getattr(Course, attr)
                # setattr(Course, attr, row[attr])
            except:
                headers.remove(attr)
                df.drop(attr, axis=1, inplace=True)

        feedback = []
        for index, row in df.iterrows():
            course = db_session.query(Course).filter(Course.termID == termID, Course.courseNum == row['courseNum'])
            # course = db_session.query(Course).filter(Course.courseNum == row['courseNum'] and Course.termID == termID)
            print(course.one_or_none())
            if course.one_or_none() == None:
                course = Course(
                    courseNum=row['courseNum'],
                    courseName=row['courseName'],
                    termID=termID,
                )

                try:
                    feedback.append("Add course {} successfully".format(row['courseNum']))

                    for attr in headers:
                        # course.attr = row[attr]
                        attribute = attr  # 用于记录错误信息
                        if str(row[attr]).lower() == 'nan' or str(row[attr]).lower() == 'nat':
                            setattr(course, attr, None)
                        elif attr == 'courseNum' or attr == 'courseName' or attr == 'termID':
                            continue
                        elif attr == 'estimatedNumOfStudents' or attr == 'currentlyNumOfStudents' or attr == 'numOfAssignments' or attr == 'numOfLabsPerWeek' or attr == 'numOfTutorialsPerWeek':
                            if not isinstance(row[attr], float) and not isinstance(row[attr], int):
                                feedback.append(
                                    "Update attribute {} failed, because `{}` has incorrect result `{}`".format(
                                        row['courseNum'], attr, row[attr]))
                            else:
                                setattr(course, attr, int(row[attr]))
                        elif attr == 'tutorResponsibility' or attr == 'markerResponsibility' or attr == 'prerequisite':
                            if not isinstance(row[attr], str):
                                feedback.append(
                                    "Update attribute {} failed, because `{}` has incorrect result `{}`".format(
                                        row['courseNum'], attr, row[attr]))
                            else:
                                setattr(course, attr, row[attr])
                        elif attr == 'needTutors' or attr == 'needMarkers' or attr == 'canPreAssign':
                            if row[attr] == 'Y':
                                setattr(course, attr, True)
                            elif row[attr] == 'N':
                                setattr(course, attr, False)
                            else:
                                feedback.append(
                                    "Update attribute {} failed, because `{}` has incorrect result `{}`".format(
                                        row['courseNum'], attr, row[attr]))
                        elif attr == 'totalAvailableHours':
                            if not isinstance(row[attr], float):
                                feedback.append(
                                    "Update attribute {} failed, because `{}` has incorrect result `{}`".format(
                                        row['courseNum'], attr, row[attr]))
                            else:
                                setattr(course, attr, row[attr])
                        elif attr == 'markerDeadLine' or attr == 'tutorDeadLine':
                            if not isinstance(row[attr], datetime.datetime):
                                feedback.append(
                                    "Update attribute {} failed, because `{}` has incorrect result `{}`".format(
                                        row['courseNum'], attr, row[attr]))
                            else:
                                setattr(course, attr, row[attr])

                        else:
                            feedback.append("Update attribute {} failed, because `{}` has incorrect result `{}`".format(
                                row['courseNum'], attr, row[attr]))
                    db_session.add(course)

                except Exception as e:
                    feedback.append("Add course {} failed".format(row['courseNum']))
            else:
                feedback.append(
                    "Add course {} fail. {} already existed in this term".format(row['courseNum'], row['courseNum']))
        db_session.commit()
        return feedback
        # return []


def get_the_course_working_hour(user: Users, course_id, roleName: str, isPublished: bool):
    role: RoleInCourse = get_RoleInCourse_by_name(roleName.lower())
    if role is None:
        return False, "Role not found", 404
    course_user: CourseUser = db_session.query(CourseUser).filter(CourseUser.userID == user.id,
                                                                  CourseUser.isPublished == isPublished,
                                                                  CourseUser.roleID == role.roleID,
                                                                  CourseUser.courseID == course_id).one_or_none()
    if course_user is None:
        return False, "Enrollment Information not found", 404
    return True, course_user.serialize_with_working_hours(), 200


def get_available_course_by_term(term_id, roleName):
    term = get_term_by_id(term_id)
    role = get_RoleInCourse_by_name(roleName.lower())
    if term is None:
        return False, "Term not found", 404
    if role is None:
        return False, "Role not found", 404
    if role.Name == 'tutor':
        courses = db_session.query(Course).filter(Course.termID == term_id, Course.needTutors).all()
    elif role.Name == 'marker':
        courses = db_session.query(Course).filter(Course.termID == term_id, Course.needMarkers).all()
    else:
        return False, "Role not found", 404
    return True, [course.serialize() for course in courses if course.getCurrentPublishedAvailableHours() > 0], 200
