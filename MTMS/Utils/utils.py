import random

from flask import Blueprint
from flask_restful import Api
from enum import Enum
import datetime



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


class StudentDegreeEnum(Enum):
    Undergraduate = 1
    Postgraduate = 2

class ApplicationStatus(Enum):
    Unsubmit = 1
    Pending = 2
    Success = 3
    Fail = 4

def response_for_services(status, mes):
    return {"status": status, "mes": mes}


def datetime_format(date: str) -> datetime:
    d = date.split('-')
    year, month, day = int(d[0]), int(d[1]), int(d[2])
    return datetime.date(year, month, day)


def filter_empty_value(arg: dict) -> dict:
    d = {}
    for key, value in arg.items():
        if value or value == 0:
            d[key] = value
    return d


def dateTimeFormat(dateTime):
    try:
        result = dateTime.isoformat()
    except:
        result = None
    return result

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




def response_for_services(status, mes):
    return {"status":status, "mes" : mes}