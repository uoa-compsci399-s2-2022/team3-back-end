from MTMS.Models.courses import CourseUser, RoleInCourse, Payday, WorkingHours
from MTMS import db_session


def modify_estimated_hours(course_id, user_id, roleName, estimated_hours):
    """
    Modify estimated hours for a user in a course
    :param course_id: course id
    :param user_id: user id
    :param roleName: role name
    :param estimated_hours: estimated hours
    :return: None
    """
    try:
        course_user = db_session.query(CourseUser).join(RoleInCourse).filter(CourseUser.courseID == course_id,
                                                                             CourseUser.userID == user_id,
                                                                             RoleInCourse.Name == roleName.lower()).first()
        if course_user:
            course_user.estimatedHours = estimated_hours
            db_session.commit()
            return True, "Success", 200
        else:
            return False, "User not found in this course", 400
    except Exception as e:
        db_session.rollback()
        return False, "Unknown error", 500


def get_RoleInCourse_by_name(roleName):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == roleName).one_or_none()
    return role


def submit_actual_working_hour(course_id, user_id, roleName, payday_id, actual_hours):
    """
    Submit actual working hour for a user in a course
    :param course_id: course id
    :param user_id: user id
    :param roleName: role name
    :param payday_id: payday id
    :param actual_hours: actual hours
    :return: None
    """
    # try:
    role: RoleInCourse = get_RoleInCourse_by_name(roleName.lower())
    if not role:
        return False, "Role not found", 400
    courseUser: CourseUser = db_session.query(CourseUser).filter(CourseUser.courseID == course_id,
                                                                CourseUser.userID == user_id,
                                                                CourseUser.roleID == role.roleID).one_or_none()
    if not courseUser:
        return False, "User not found in this course", 400
    workingHours: WorkingHours = db_session.query(WorkingHours).filter(
        WorkingHours.courseID == course_id,
        WorkingHours.userID == user_id,
        WorkingHours.roleID == role.roleID, WorkingHours.paydayID == payday_id).first()
    if workingHours:
        workingHours.actualHours = actual_hours
        db_session.commit()
        return True, "Success", 200
    else:
        workingHours = WorkingHours(courseID=course_id, userID=user_id, roleID=role.roleID, paydayID=payday_id,
                                    actualHours=actual_hours)
        db_session.add(workingHours)
        db_session.commit()
        return True, "Success", 200
    # except Exception as e:
    #     db_session.rollback()
    #     return False, "Unknown error", 400
