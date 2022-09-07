import random

from flask import Blueprint
from flask_restful import Api
import enum
import datetime


def register_api_blueprints(app, blueprint_name, blueprint_importName, resource:list):
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

class ProfileTypeEnum(enum.Enum):
    Integer = 1
    String = 2
    Double = 3
    MultipleChoice = 4
    Boolean = 5
    File = 6
    Email = 7

def response_for_services(status, mes):
    return {"status":status, "mes" : mes}


def valid_semester_format(semester):
    if semester in ['Semester One', 'Semester Two', 'Summer Semester']:
        return True
    else:
        return False

def datetime_format(date:str) -> datetime:
    d = date.split('-')
    year, month, day = int(d[0]), int(d[1]), int(d[2])
    return datetime.date(year, month, day)


def filter_empty_value(arg:dict) -> dict:
    d = {}  # filter the empty value
    for key, value in arg.items():
        if value != None:
            d[key] = value

    return d

def generate_validation_code():  # generate a random 6-digit number, uprdate it after
    list_res = []
    for i in range(0,6):
        n = random.randint(0, 2)
        if (n == 0):
            list_res.append(str(random.randint(0, 9)))
        elif (n == 1):
            list_res.append(chr(random.randrange(65, 90)))
        elif (n == 2):
            list_res.append(chr(random.randrange(97, 122)))
    return ''.join(list_res)



