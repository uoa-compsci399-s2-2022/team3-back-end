import datetime
from email.header import Header
from email.mime.text import MIMEText

from flask import current_app
from werkzeug.security import check_password_hash
from MTMS import db_session, cache
from MTMS.Management.services import add_group
from MTMS.Models.applications import Validation_code
from MTMS.Models.users import Users, Permission, Groups
import jwt
from flask_httpauth import HTTPTokenAuth
from MTMS.settings import *
from MTMS.Utils.utils import response_for_services, generate_validation_code
import smtplib
auth = HTTPTokenAuth('Bearer')


# Authentication
@auth.verify_token
def verify_token(token):
    key = current_app.config['SECRET_KEY']
    if is_overdue_token(token):
        return False
    try:
        data = jwt.decode(token, key, algorithms="HS256")
    except jwt.ExpiredSignatureError:
        print("The Token expired")
        return False
    except:
        return False
    if 'id' in data:
        return get_user_by_id(data['id'])


def authenticate(id, password):
    user = db_session.query(Users).filter(Users.id == id).one_or_none()
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
    if token in [i[1] for i in overdue_token]:
        return True
    return False


# Authorization
@auth.get_user_roles
def get_user_roles(user: Users):
    return [g.groupName for g in user.groups]

def get_permission_group(permission):
    pm:Permission = db_session.query(Permission).filter(Permission.name == permission).one_or_none()
    if pm:
        return [g.groupName for g in pm.groups]



# User
def get_user_by_id(id):
    user = db_session.query(Users).filter(Users.id == id).one_or_none()
    return user


def get_all_users():
    user = db_session.query(Users).all()
    return user


# the validation email will generate a code and send to the user's email
# the code will be used to validate the user's email
def send_validation_email(email):
    try:
        sender = DEFAULT_SENDER
        receivers = [email]
        sender_pwd = DEFAULT_SENDER_PASSWORD
        if ADMIN_SENDER != "":
            sender = ADMIN_SENDER
            sender_pwd = ADMIN_SENDER_PASSWORD

        smtp = smtplib.SMTP(HOST_SEVER, PORT_SEVER)

        # check the smtp is connected, delete the print later
        print(smtp.ehlo())
        print(smtp.starttls())
        print(smtp.login(sender, sender_pwd))

        code = generate_validation_code()
        message = DEFAULT_MESSAGE + ''.join(code)

        mes = MIMEText(message, 'plain', 'utf-8')
        mes['From'] = Header('MTMS', 'utf-8')
        mes['To'] = Header(email, 'utf-8')
        mes['Subject'] = Header('Validation Code', 'utf-8')

        print(smtp.sendmail(sender, receivers, mes.as_string()))
        print("send email successfully")

        # save the code to the database, and the code will be expired and it depends on our front end
        if db_session.query(Validation_code).filter(Validation_code.email == email).one_or_none():
            db_session.query(Validation_code).filter(Validation_code.email == email).delete()
            db_session.commit()

        # once we register successfully, we will delete the code in the database
        db_session.add(Validation_code(email=email, code =code))
        db_session.commit()
        #smtp.quit()
        return response_for_services(
            True, code
        )
    except:
        return response_for_services(
            False, "fail, check your email address"
        )



# 后期安排 120s 自动删除过期的验证码， 前端设置60s 输入验证码
def delete_validation_code(email):
    db_session.query(Validation_code).filter(Validation_code.email == email).delete()
    db_session.commit()
    return response_for_services(
        True, "delete successfully"
    )

def register_user(user: Users ,code:str):
    email = user.email
    check_send_validation_email = db_session.query(Validation_code).filter(Validation_code.email == email).one_or_none()
    if check_send_validation_email == None :
        return response_for_services(
            'False', 'please send the validation code first'
        )
    else:
        if check_send_validation_email.code == code:
            group = db_session.query(Groups).filter(Groups.groupName == 'student').one_or_none()  # default group is student

            db_session.add(user)
            add_group(user, group)
            db_session.commit()



            # 删除验证码
            delete_validation_code(email)
            print('delete successfully')
            return response_for_services(
                True, 'register successfully'
            )
        else:
            return response_for_services(
                False, 'wrong validation code'
            )

def Exist_userID(id):
    user = db_session.query(Users).filter(Users.id == id).one_or_none()
    if user:
        return True
    else:
        return False

def Exist_user_Email(email):
    user = db_session.query(Users).filter(Users.email == email).one_or_none()
    if user:
        return True
    else:
        return False