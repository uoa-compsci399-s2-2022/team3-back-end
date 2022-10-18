import datetime
import json
import re

from email_validator import validate_email, EmailNotValidError
from cerberus import Validator
from flask_restful.fields import DateTime

from MTMS.Models.courses import Course

GRADE = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "CPL", "Pass", "D+", "D", "D-", "DNC", "DNS", "Fail"]


def empty_or_email(email_str):
    if email_str is None:
        raise ValueError('{} is not a valid email'.format(email_str))
    if not email_str.strip():
        return email_str
    try:
        validate_email(email_str)
        return email_str
    except EmailNotValidError:
        raise ValueError('{} is not a valid email'.format(email_str))


def email(email_str):
    try:
        validate_email(email_str)
        return email_str
    except EmailNotValidError:
        raise ValueError('{} is not a valid email'.format(email_str))


def is_email(email_str):
    try:
        validate_email(email_str)
        return True
    except EmailNotValidError:
        return False
    except AttributeError:
        return False


def non_empty_string(s):
    try:
        s = s.strip()
        if not s:
            raise ValueError("Must not be empty string")
        return s
    except:
        raise ValueError("Must not be empty string")


def grade(grade_str):
    if grade_str in GRADE:
        return grade_str
    else:
        raise ValueError(f'{grade_str} is not a valid grade')


def application_course_list(list):
    LEARNED_SCHEMA = {
        'courseid': {'required': True, 'type': 'integer'},
        'haslearned': {'required': True, 'type': 'boolean'},
        'grade': {'required': True, 'type': 'string'},
        'preexperience': {'required': True, 'type': 'string'},
        'preference': {'required': True, 'type': 'integer'},
    }
    NON_LEARNED_SCHEMA = {
        'courseid': {'required': True, 'type': 'integer'},
        'haslearned': {'required': True, 'type': 'boolean'},
        'explanation': {'required': True, 'type': 'string'},
        'preexperience': {'required': True, 'type': 'string'},
        'preference': {'required': True, 'type': 'integer'},
    }
    for c in list:
        lower_temp_dict = {}
        for k in c:
            lower_temp_dict[k.lower()] = c[k]
        if "haslearned" not in lower_temp_dict.keys():
            raise ValueError('haslearned must be existed')
        elif type(lower_temp_dict["haslearned"]) != bool:
            raise ValueError('haslearned must be boolean')

        if lower_temp_dict["haslearned"]:
            v = Validator(LEARNED_SCHEMA)
            if not v.validate(lower_temp_dict):
                raise ValueError(json.dumps(v.errors))
        else:
            v = Validator(NON_LEARNED_SCHEMA)
            if not v.validate(lower_temp_dict):
                raise ValueError(json.dumps(v.errors))

        if lower_temp_dict["grade"] not in GRADE:
            raise ValueError(f"{lower_temp_dict['grade']} is not a valid grade")
    return list


def is_UOA_email_format(email):
    email = email.split('@auckland.ac.nz')
    if len(email) == 2 and email[1] == '':
        return True
    else:
        return False


def validCourseType(course: Course):
    if not isinstance(course.totalAvailableHours, float) or not isinstance(course.estimatedNumOfStudents,
                                                                           int) or not isinstance(
            course.currentlyNumOfStudents, int) or not isinstance(course.needTutors, bool) \
            or not isinstance(course.needMarkers, bool) or not isinstance(course.numOfAssignments,
                                                                          int) or not isinstance(
        course.numOfLabsPerWeek, int) or not isinstance(course.numOfTutorialsPerWeek, int) \
            or not isinstance(course.canPreAssign, bool) or not isinstance(course.applications, list) or not isinstance(
        course.course_users,
        list) or not isinstance(
        course.markerDeadLine, DateTime) or not isinstance(course.tutorDeadLine, DateTime) \
            or not isinstance(course.prerequisite, str):
        return False
    else:
        return True


def validCourseType2(data, course):
    if data == 'totalAvailableHours' and not isinstance(course.totalAvailableHours, float):
        return False
    elif data == 'estimatedNumOfStudents' and not isinstance(course.estimatedNumOfStudents, int):
        return False
    elif data == 'currentlyNumOfStudents' and not isinstance(course.currentlyNumOfStudents, int):
        return False
    elif data == 'needTutors' and not isinstance(course.needTutors, bool):
        return False
    elif data == 'needMarkers' and not isinstance(course.needMarkers, bool):
        return False
    elif data == 'numOfAssignments' and not isinstance(course.numOfAssignments, int):
        return False
    elif data == 'numOfLabsPerWeek' and not isinstance(course.numOfLabsPerWeek, int):
        return False
    elif data == 'numOfTutorialsPerWeek' and not isinstance(course.numOfTutorialsPerWeek, int):
        return False
    elif data == 'canPreAssign' and not isinstance(course.canPreAssign, bool):
        return False
    elif data == 'applications' and not isinstance(course.applications, list):
        return False
    elif data == 'course_users' and not isinstance(course.course_users, list):
        return False
    elif data == 'markerDeadLine' and not isinstance(course.markerDeadLine, datetime.datetime):
        return False
    elif data == 'tutorDeadLine' and not isinstance(course.tutorDeadLine, datetime.datetime):
        return False
    elif data == 'prerequisite' and not isinstance(course.prerequisite, str):

        return False
    elif data == 'markerResponsibility' and not isinstance(course.markerResponsibility, str):
        return False
    elif data == 'tutorResponsibility' and not isinstance(course.tutorResponsibility, str):
        return False
    else:
        return True


course = Course(
    courseName="COMPSCI 101",
    courseNum="101",
    termID=1,
    estimatedNumOfStudents=4312,
    markerDeadLine=datetime.datetime.strptime("2020/10/10", "%Y/%m/%d"),
)
print(course.markerDeadLine)
