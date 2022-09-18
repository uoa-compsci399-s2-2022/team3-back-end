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


class ProfileTypeEnum(Enum):
    Integer = 1
    String = 2
    Double = 3
    MultipleChoice = 4
    Boolean = 5
    File = 6
    Email = 7

class CourseApplicationStatus(Enum):
    Pending = 1
    Success = 2
    Fail = 3




def response_for_services(status, mes):
    return {"status": status, "mes": mes}


def datetime_format(date: str) -> datetime:
    d = date.split('-')
    year, month, day = int(d[0]), int(d[1]), int(d[2])
    return datetime.date(year, month, day)


def filter_empty_value(arg: dict) -> dict:
    d = {}
    for key, value in arg.items():
        if value:
            d[key] = value
<<<<<<< HEAD:MTMS/utils/utils.py
    return d


def dateTimeFormat(dateTime):
    try:
        result = dateTime.isoformat()
    except:
        result = None
    return result
=======

    return d
>>>>>>> parent of 9471290 (add register function):MTMS/Utils/utils.py
