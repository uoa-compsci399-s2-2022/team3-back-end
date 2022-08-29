import datetime
from flask import current_app
from werkzeug.security import check_password_hash
from MTMS import db_session, cache
from MTMS.model import User
import jwt
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth('Bearer')


@auth.verify_token
def verify_token(token):
    key = current_app.config['SECRET_KEY']
    if is_overdue_token(token):
        return False
    try:
        data = jwt.decode(token, key, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        print("The Token expired")
    except:
        return False
    if 'id' in data:
        return get_user_by_id(data['id'])


def get_user_by_id(id):
    user = db_session.query(User).filter(User.id == id).one_or_none()
    return user


def authenticate(id, password):
    user = db_session.query(User).filter(User.id == id).one_or_none()
    if user and check_password_hash(user.password, password):
        return user


def generate_token(user, operation=None, **kwargs):
    """ Generate for mailbox validation JWT（json web token）"""
    #  The key used for the signature
    key = current_app.config['SECRET_KEY']
    #  Data load to be signed
    data = {"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
        seconds=int(current_app.config["TOKEN_EXPIRATION"])),
            'id': user.id, 'operation': operation}
    data.update(**kwargs)
    print(data)
    return jwt.encode(data, key, algorithm="HS256")


def add_overdue_token(token):
    overdue_token = cache.get("overdue_token")
    for i in range(len(overdue_token)):
        if datetime.datetime.now() - datetime.timedelta(seconds=int(current_app.config["TOKEN_EXPIRATION"]) * 2) > \
                overdue_token[i][0]:
            overdue_token.pop(i)
            i -= 1
    overdue_token.append([datetime.datetime.now(), token])
    cache.set("overdue_token", overdue_token)



def is_overdue_token(token):
    overdue_token = cache.get("overdue_token")
    print(overdue_token)
    if token in [i[1] for i in overdue_token]:
        return True
    return False
