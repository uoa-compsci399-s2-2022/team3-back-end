import random

from flask import Blueprint
from flask_restful import Api
import datetime


def get_grade_GPA(grade):
    if grade is None:
        return None
    GRADE = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "CPL", "Pass", "D+", "D", "D-", "DNC", "DNS", "Fail"]
    gpa = [9, 8, 7, 6, 5, 4, 3, 2, 1, None, None, 0, 0, 0, 0, 0, 0]
    return gpa[GRADE.index(grade)]


def get_average_gpa(grade_list):
    gpa_list = []
    for i in range(len(grade_list)):
        if get_grade_GPA(grade_list[i]) is not None:
            gpa_list.append(get_grade_GPA(grade_list[i]))
    if len(gpa_list) == 0:
        return 0
    return sum(gpa_list) / len(gpa_list)


def register_api_blueprints(app, blueprint_name, blueprint_importName, resource: list):
    test_api_bp = Blueprint(blueprint_name, blueprint_importName)
    api = Api(test_api_bp)
    for r in resource:
        if len(r) == 4:
            api.add_resource(r[0], r[1], methods=r[2], endpoint=r[3])
        elif len(r) == 2:
            api.add_resource(r[0], r[1])
        else:
            raise IndexError
    app.register_blueprint(test_api_bp)


def get_user_by_id(id):
    from MTMS.Models.users import Users
    from MTMS import db_session
    user = db_session.query(Users).filter(Users.id == id).one_or_none()
    return user


def response_for_services(status, mes):
    return {"status": status, "mes": mes}


def datetime_format(date: str) -> datetime:
    d = date.split('-')
    year, month, day = int(d[0]), int(d[1]), int(d[2])
    return datetime.date(year, month, day)


def filter_empty_value(arg: dict) -> dict:
    d = {}
    for key, value in arg.items():
        if (isinstance(value, str) and value.strip() == "") or value is None:
            continue
        d[key] = value
    return d


def dateTimeFormat(dateTime):
    try:
        result = dateTime.isoformat()
        result = result + 'Z'
    except:
        result = None
    return result


def generate_validation_code():  # generate a random 6-digit number, uprdate it after
    list_res = []
    for i in range(0, 6):
        n = random.randint(0, 2)
        if (n == 0):
            list_res.append(str(random.randint(0, 9)))
        elif (n == 1):
            list_res.append(chr(random.randrange(65, 90)))
        elif (n == 2):
            list_res.append(chr(random.randrange(97, 122)))
    return ''.join(list_res)


def generate_random_password():
    list_res = []
    for i in range(0, 12):
        n = random.randint(0, 2)
        if (n == 0):
            list_res.append(str(random.randint(0, 9)))
        elif (n == 1):
            list_res.append(chr(random.randrange(65, 90)))
        elif (n == 2):
            list_res.append(chr(random.randrange(97, 122)))
    return ''.join(list_res)


def get_all_settings():
    from MTMS.Models.setting import Setting
    from MTMS import db_session
    settings = db_session.query(Setting).filter(Setting.settingID == 1).first()
    return settings


def get_course_by_id(courseID):
    from MTMS.Models.courses import Course
    from MTMS import db_session
    return db_session.query(Course).filter(Course.courseID == courseID).one_or_none()