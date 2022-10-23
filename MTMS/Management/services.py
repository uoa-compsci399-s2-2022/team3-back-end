from flask import current_app

from MTMS import db_session
from MTMS.Models.users import Users, Groups
from MTMS.Models.courses import RoleInCourse, CourseUser
from MTMS.Models.setting import Setting
from MTMS import cache
from celery.result import AsyncResult

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


# RoleInCourse
def add_RoleInCourse(Name):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == Name).first()
    if role == None:
        role = RoleInCourse()
        role.Name = Name
        db_session.add(role)
        db_session.commit()
        return (True, "add '{}' successfully".format(Name), 200)
    else:
        return (False, "'{}' already existed".format(Name), 400)


def get_All_RoleInCourse():
    role = db_session.query(RoleInCourse).all()
    result = []
    for r in role:
        result.append(r.serialize())
    return result


def get_RoleInCourse_by_name(roleName):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == roleName).one_or_none()
    return role


def get_RoleInCourse_by_id(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID).one_or_none()
    return role


def delete_RoleInCourse(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID)
    if role.first() == None:
        return (False, "'{}' does not existed".format(roleID), 404)
    else:
        role.delete()
        db_session.commit()
        return (True, "delete '{}' successfully".format(roleID), 200)


def modify_RoleInCourse(args: dict):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == args['roleID'])
    if role.first() == None:
        return (False, "'{}' does not existed".format(args['roleID']), 404)
    else:
        for key, value in args.items():
            role.update(
                {key: value}
            )
        db_session.commit()
        return (True, "INFO:  update '{}' successfully".format(args['roleID']), 200)


def get_user_by_courseID(courseID):
    users = db_session.query(CourseUser).filter(CourseUser.courseID == courseID).all()
    return users


def get_user_by_courseID_roleID(courseID, roleID):
    course_users = db_session.query(CourseUser).filter(
        CourseUser.courseID == courseID and CourseUser.roleID == roleID).all()
    users = []
    for i in course_users:
        users.append(i.user)
    return users


def get_all_settings():
    settings = db_session.query(Setting).filter(Setting.settingID == 1).first()
    return settings.serialize()


def modify_setting(args: dict):
    setting = db_session.query(Setting).filter(Setting.settingID == 1).first()
    if setting is None:
        return False, "An error occurred with the server's setting module", 400
    else:
        for key, value in args.items():
            if hasattr(setting, key):
                setattr(setting, key, value)
            else:
                db_session.rollback()
                return False, "Save the setting error", 400
        db_session.commit()
        return True, 'Update setting successful!', 200


def get_user_sending_status(user: Users):
    result = []
    for i in user.SenderEmailDeliveryStatus:
        i_serialized = i.serialize()
        if not current_app.config["CELERY_BROKER_URL"] or not current_app.config["CELERY_BROKER_URL"].strip():
            i_serialized.update({'celery_task_status': "No Deploy to the system"})
        elif i.task_id is not None:
            status = AsyncResult(i.task_id)
            i_serialized.update({'celery_task_status': status.status})
        result.append(i_serialized)
    return result

# def Send_Email(users, message):
#     '''
#     :param users: list of users
#     :param content: content of email
#     '''
#     users_email = []
#     for user in users:
#         users_email.append(user.email)
#
#     print(users_email)
#     sender = DEFAULT_SENDER
#     receivers = users_email
#     sender_pwd = DEFAULT_SENDER_PASSWORD
#     if ADMIN_SENDER != "":
#         sender = ADMIN_SENDER
#         sender_pwd = ADMIN_SENDER_PASSWORD
#
#     smtp = smtplib.SMTP(HOST_SEVER, PORT_SEVER)
#
#     try:
#     # check the smtp is connected, delete the print later
#         print(smtp.ehlo())
#         print(smtp.starttls())
#         print(smtp.login(sender, sender_pwd))
#     except:
#         return (False, "SMTP server error", 500)
#
#
#     else:
#         mes = MIMEText(message, 'plain', 'utf-8')
#         mes['From'] = Header('MTMS', 'utf-8')
#         mes['To'] = Header(','.join(users_email), 'utf-8')
#         mes['Subject'] = Header('no-reply', 'utf-8')
#
#         print(smtp.sendmail(sender, receivers, mes.as_string()))
#         print("send email successfully")
#         return (True, "send email successfully", 200)
#
