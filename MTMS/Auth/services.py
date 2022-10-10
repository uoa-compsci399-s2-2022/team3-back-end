import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import current_app
from werkzeug.security import check_password_hash
from MTMS import db_session, cache
from MTMS.Models.users import Users, Permission, Groups
import jwt
from flask_httpauth import HTTPTokenAuth
from MTMS.Utils.utils import response_for_services, generate_validation_code
import smtplib
import os
from jinja2 import Template

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
    pm: Permission = db_session.query(Permission).filter(Permission.name == permission).one_or_none()
    if pm:
        return [g.groupName for g in pm.groups]


def check_user_permission(user: Users, permission):
    return len(set([g.groupName for g in user.groups]) & set(get_permission_group(permission))) > 0


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
    sender = current_app.config["EMAIL_ADDRESS"]
    sender_pwd = current_app.config["EMAIL_PASSWORD"]
    smtp = smtplib.SMTP(current_app.config["EMAIL_SERVER_HOST"], current_app.config["EMAIL_SERVER_PORT"])
    # check the smtp is connected, delete the print later
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, sender_pwd)
    code = generate_validation_code()
    # Get EmailTemplate Path
    path = os.path.join(os.path.dirname(current_app.instance_path), "MTMS", "EmailTemplate")

    # Define msg root
    mes = MIMEMultipart('related')
    mes['From'] = Header('MTMS - The University of Auckland', 'utf-8')
    mes['To'] = Header(email, 'utf-8')
    mes['Subject'] = Header('Verification Code', 'utf-8')

    # load html file
    html_path = os.path.join(path, "VerificationCodeEmailTemplate.html")
    html_file = open(html_path, "r", encoding="utf-8")
    html = html_file.read()
    html_file.close()
    tmpl = Template(html)
    html = tmpl.render(code=code)
    mesHTML = MIMEText(html, 'html', 'utf-8')
    mes.attach(mesHTML)

    # load uoa logo
    image_path = os.path.join(path, "uoa-logo.png")
    image_file = open(image_path, 'rb')
    msgImage = MIMEImage(image_file.read())
    image_file.close()
    msgImage.add_header('Content-ID', '<image1>')
    mes.attach(msgImage)

    smtp.sendmail(sender, email, mes.as_string())
    print("send email successfully")

    email_validation_code = cache.get("email_validation_code")
    status = 0
    for i in email_validation_code:
        if i["email"] == email:
            i["code"] = code
            i["date"] = datetime.datetime.now()
            status = 1
            break

    if status == 0:
        email_validation_code.append({"email": email, "code": code, "date": datetime.datetime.now()})
    cache.set("email_validation_code", email_validation_code)

    # smtp.quit()
    return response_for_services(
        True, code
    )


# 后期安排 120s 自动删除过期的验证码， 前端设置60s 输入验证码
def delete_validation_code(email):
    email_validation_code = cache.get("email_validation_code")
    for i in email_validation_code:
        if i["email"] == email:
            email_validation_code.remove(i)
            break
    cache.set("email_validation_code", email_validation_code)
    return response_for_services(
        True, "delete successfully"
    )


def register_user(user: Users, code: str):
    email = user.email
    email_validation_code = cache.get("email_validation_code")
    check_send_validation_email = None
    for i in email_validation_code:
        if i["email"] == email:
            check_send_validation_email = i
            email_validation_code.remove(i)
            cache.set("email_validation_code", email_validation_code)
            break

    if check_send_validation_email is None:
        return response_for_services(
            False, 'please send the validation code first'
        )
    else:
        if check_send_validation_email["code"] == code:
            group = db_session.query(Groups).filter(
                Groups.groupName == 'student').one_or_none()  # default group is student
            user.groups.append(group)
            db_session.add(user)
            db_session.commit()
            return response_for_services(
                True, 'register successfully'
            )
        else:
            return response_for_services(
                False, 'wrong validation code'
            )


def validate_code_though_email(email, code):
    email_validation_code = cache.get("email_validation_code")
    # print(email_validation_code)
    check_send_validation_email = None
    for i in email_validation_code:
        if i["email"] == email:
            check_send_validation_email = i
            break

    if check_send_validation_email is None:
        return response_for_services(
            False, 'please send the validation code first'
        )
    else:
        if check_send_validation_email["code"] == code:
            return response_for_services(
                True, 'correct validation code'
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
    user = db_session.query(Users).filter(Users.email == email).first()
    if user:
        return True
    else:
        return False


def get_all_groups():
    groups = db_session.query(Groups).all()
    return groups
