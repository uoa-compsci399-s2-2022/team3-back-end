from MTMS.Models.courses import CourseUser, RoleInCourse
from MTMS import db_session
from sqlalchemy.orm import query


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
