import datetime
from flask import current_app
from werkzeug.security import check_password_hash
from MTMS import db_session, cache
from MTMS.model import Users, Groups
import jwt
from flask_httpauth import HTTPTokenAuth




def get_user_by_id(id):
    user = db_session.query(Users).filter(Users.id == id).one_or_none()
    return user


def get_group_by_name(name):
    group = db_session.query(Groups).filter(Groups.groupName == name).one_or_none()
    return group


def add_group(user, group):
    user.groups.append(group)
    db_session.commit()

def delete_group(user, group):
    user.groups.remove(group)
    db_session.commit()