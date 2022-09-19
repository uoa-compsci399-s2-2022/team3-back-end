import smtplib
from email.header import Header
from email.mime.text import MIMEText

from MTMS import db_session
from MTMS.Models.users import Users, Groups
from MTMS.Models.courses import RoleInCourse, CourseUser
from MTMS.Utils.utils import response_for_services

from MTMS.settings import *

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

def get_user_by_courseID_roleID(courseID, roleID) -> list[Users]:
    course_users = db_session.query(CourseUser).filter(CourseUser.courseID == courseID and CourseUser.roleID == roleID).all()
    users = []
    for i in course_users:
        users.append(i.user)
    return users


def Send_Email(users, message):
    '''
    :param users: list of users
    :param content: content of email
    '''
    users_email = []
    for user in users:
        users_email.append(user.email)

    print(users_email)
    sender = DEFAULT_SENDER
    receivers = users_email
    sender_pwd = DEFAULT_SENDER_PASSWORD
    if ADMIN_SENDER != "":
        sender = ADMIN_SENDER
        sender_pwd = ADMIN_SENDER_PASSWORD

    smtp = smtplib.SMTP(HOST_SEVER, PORT_SEVER)

    try:
    # check the smtp is connected, delete the print later
        print(smtp.ehlo())
        print(smtp.starttls())
        print(smtp.login(sender, sender_pwd))
    except:
        return (False, "SMTP server error", 500)


    else:
        mes = MIMEText(message, 'plain', 'utf-8')
        mes['From'] = Header('MTMS', 'utf-8')
        mes['To'] = Header(','.join(users_email), 'utf-8')
        mes['Subject'] = Header('no-reply', 'utf-8')

        print(smtp.sendmail(sender, receivers, mes.as_string()))
        print("send email successfully")
        return (True, "send email successfully", 200)

