import datetime
import os

import pandas as pd
from flask_restful.fields import DateTime

from MTMS import db_session
from MTMS.Models.courses import CourseUser
from MTMS.Models.users import Users
from MTMS.Models.courses import Course, Term, RoleInCourse
from MTMS.Utils.utils import response_for_services
from sqlalchemy import distinct


# Course
from MTMS.Utils.validator import validCourseType, validCourseType2


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
        return True, f"delete termID:{termID} successfully", 200
    else:
        return False, f"termID:{termID} does not existed", 404


def get_Allterms():
    terms = db_session.query(Term).all()
    terms_list = []
    for i in range(len(terms)):
        terms_list.append(terms[i].serialize())
    return terms_list


def get_available_term():
    terms = db_session.query(Term).filter(Term.isAvailable == True).all()
    terms_list = []
    for i in range(len(terms)):
        terms_list.append(terms[i].serialize())
    return terms_list


def modify_Term(termID, modify_info):
    term = get_term_by_id(termID)
    if not term:
        return False, "{} does not existed".format(termID), 404
    else:
        term = db_session.query(Term).filter(
            Term.termID == termID
        )
        for key, value in modify_info.items():
            term.update(
                {key: value}
            )
        db_session.commit()
        return True, "update {} successfully".format(termID), 200


# Enrolment (That is, the correspondence between each course and the user)
def add_CourseUser(courseID, userID, roleName):
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
            isPublished=True
        )
        db_session.add(course_user)
        db_session.commit()
        return True, "Successful Enrolment", 200
    except:
        return False, "Unexpected Error", 400


def modify_CourseUser(course, user: Users, role):
    courseUser: list[CourseUser] = db_session.query(CourseUser).filter(CourseUser.courseID == course.courseID,
                                                                       CourseUser.userID == user.id).all()
    for cu in courseUser:
        db_session.delete(cu)

    for roleName in role:
        role = get_RoleInCourse_by_name(roleName)
        if role is None:
            db_session.rollback()
            return False, f"role '{roleName}' does not existed", 404
        course_user = CourseUser(
            courseID=course.courseID,
            userID=user.id,
            roleID=role.roleID,
            isPublished=True
        )
        db_session.add(course_user)
    db_session.commit()
    return True, "update role successfully", 200


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
            "termName": cu.course.term.termName,
            "termID": cu.course.termID,
            "courseName": cu.course.courseName,
        })
    return result


def get_user_enrolment_in_term(userID, termID):
    course_user = db_session.query(CourseUser).join(Course).filter(
        Course.termID == termID, CourseUser.userID == userID, CourseUser.isPublished == True).all()
    return course_user


def get_course_user(courseID, isPublished):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID,
                                                      CourseUser.isPublished == isPublished).all()
    result = []
    for i in course_user:
        user_dict = i.user.profile_serialize()
        user_dict.update({"roleInCourse": i.role.Name})
        result.append(user_dict)
    return result


def get_course_user_with_public_information(courseID):
    course_user = db_session.query(CourseUser).filter(CourseUser.courseID == courseID).all()
    result = []
    for i in course_user:
        user_dict = i.user.profile_serialize()
        user_dict.update({"roleInCourse": i.role.Name, "isPublished": i.isPublished})
        result.append(user_dict)
    return result


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
    course_user = db_session.query(CourseUser).filter(CourseUser.userID == userID, CourseUser.isPublished).all()
    result = []
    for i in course_user:
        if i.course.termID == termID:
            result.append(i.serialize())
    return result


def get_user_term(userID):
    userTerm = db_session.query(Term).join(Course).join(CourseUser).filter(CourseUser.userID == userID,
                                                                           CourseUser.isPublished).all()

    return [i.serialize() for i in userTerm]


def get_term_now():
    term = db_session.query(Term).filter(Term.startDate < datetime.datetime.now(),
                                         Term.endDate > datetime.datetime.now()).all()
    return [i.serialize() for i in term]


def Load_Courses(termID, filestream):
    df = pd.read_excel(filestream)
    headers = df.columns.values.tolist()
    if 'courseNum' not in headers or 'courseName' not in headers: # 未找到必传参数
        return False
    else:
        for i in range(len(headers)-1,-1,-1):
            attr = headers[i]
            try:
                getattr(Course, attr)
                # setattr(Course, attr, row[attr])
            except:
                headers.remove(attr)
                df.drop(attr, axis=1, inplace=True)


        feedback = []
        for index, row in df.iterrows():
            course = db_session.query(Course).filter(Course.termID == termID, Course.courseNum == row['courseNum'] )
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
                        attribute = attr    # 用于记录错误信息
                        if str(row[attr]).lower()== 'nan' or str(row[attr]).lower() =='nat':
                            setattr(course, attr, None)
                        elif attr == 'courseNum' or attr == 'courseName' or attr == 'termID':
                            continue
                        elif attr == 'estimatedNumOfStudents' or attr == 'currentlyNumOfStudents' or  attr == 'numOfAssignments' or attr == 'numOfLabsPerWeek' or attr == 'numOfTutorialsPerWeek':
                            if not isinstance(row[attr], float) and not isinstance(row[attr], int):
                                feedback.append("Update attribute {} failed, because `{}` has incorrect result `{}`".format(row['courseNum'],attr, row[attr]))
                            else:
                                setattr(course, attr, int(row[attr]))
                        elif attr == 'tutorResponsibility' or attr == 'markerResponsibility' or attr == 'prerequisite':
                            if not isinstance(row[attr], str):
                                feedback.append("Update attribute {} failed, because `{}` has incorrect result `{}`".format(row['courseNum'],attr, row[attr]))
                            else:
                                setattr(course, attr, row[attr])
                        elif attr == 'needTutors' or attr == 'needMarkers' or attr == 'canPreAssign' :
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
                                feedback.append("Update attribute {} failed, because `{}` has incorrect result `{}`".format(row['courseNum'],attr, row[attr]))
                            else:
                                setattr(course, attr, row[attr])
                        elif attr == 'markerDeadLine' or attr == 'tutorDeadLine':
                            if not isinstance(row[attr], datetime.datetime):
                                feedback.append("Update attribute {} failed, because `{}` has incorrect result `{}`".format(row['courseNum'],attr, row[attr]))
                            else:
                                setattr(course, attr, row[attr])

                        else:
                            feedback.append("Update attribute {} failed, because `{}` has incorrect result `{}`".format(row['courseNum'],attr, row[attr]))
                    db_session.add(course)

                except Exception as e:
                    feedback.append("Add course {} failed".format(row['courseNum']))
            else:
                feedback.append("Add course {} fail. {} already existed in this term".format(row['courseNum'],row['courseNum']))
        db_session.commit()
        return feedback
        # return []

