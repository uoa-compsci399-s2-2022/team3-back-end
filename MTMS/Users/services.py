import os
import smtplib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app
from jinja2 import Template

from MTMS.Models.setting import Email_Delivery_Status
from MTMS.Models.users import Groups, InviteUserSaved, Users
from MTMS.Utils.validator import empty_or_email
from MTMS import db_session
from MTMS.Utils.utils import get_user_by_id, filter_empty_value, generate_validation_code, create_email_sending_status, \
    generate_random_password
from MTMS.Auth.services import check_invitation_permission
from MTMS.Utils.enums import StudentDegreeEnum, EmailCategory, EmailStatus
from sqlalchemy import or_


def change_user_profile(user, args):
    if user is None:
        return False, "The user for this application does not exist", 404
    args = filter_empty_value(args)
    if not args:
        return False, "Did not give any valid user profile", 400
    for k in args:
        if k == "studentDegree" and args[k] is None:
            continue
        elif k == "studentDegree" and args[k] not in [i.name for i in StudentDegreeEnum]:
            return False, "Invalid student degree", 400
        try:
            getattr(user, k)
            setattr(user, k, args[k])
        except AttributeError:
            db_session.rollback()
            return False, f"Invalid field name: {k}", 400
        except ValueError as e:
            db_session.rollback()
            return False, str(e), 400
    db_session.commit()
    return True, None, None


def get_group_by_name(name):
    group = db_session.query(Groups).filter(Groups.groupName == name).one_or_none()
    return group


def save_attr_ius(i, ius, currentUser):
    try:
        for k in i:
            if k in ['_X_ROW_KEY', 'index']:
                continue
            elif k == 'email':
                try:
                    empty_or_email(i[k])
                    ius.email = i[k]
                    continue
                except ValueError as e:
                    db_session.rollback()
                    return False, e.args[0], 400
            elif k == 'userID':
                if get_user_by_id(i[k]):
                    db_session.rollback()
                    return False, "User ID already exists", 400
                ius.userID = i[k]
                continue
            elif k == 'groups':
                if not i[k]:
                    ius.Groups = []
                    continue
                ius.Groups = []
                for g in i[k]:
                    group = get_group_by_name(g)
                    if not group:
                        db_session.rollback()
                        return False, "Group not found", 404
                    if not check_invitation_permission(currentUser, group):
                        db_session.rollback()
                        return False, f"You do not have permission to invite '{group.groupName}' group", 403
                    ius.Groups.append(group)
            else:
                if hasattr(ius, k):
                    setattr(ius, k, i[k])
                else:
                    db_session.rollback()
                    return False, f"Update Records Error: The column '{k}' was not found", 404
        return True, None, None
    except Exception as e:
        db_session.rollback()
        return False, str(e), 500


def validate_ius(iusList, currentUser):
    for i in iusList:
        if not i.email:
            return False, "Email is empty", 400
        try:
            empty_or_email(i.email)
        except ValueError as e:
            return False, e.args[0], 400

        if not i.userID:
            return False, "User ID is empty", 400

        if get_user_by_id(i.userID):
            return False, f"User ID: {i.userID} already exists", 400

        if not i.name:
            return False, "Name is empty", 400

        if not i.Groups:
            return False, "Groups is empty", 400

        for g in i.Groups:
            if not check_invitation_permission(currentUser, g):
                return False, f"You do not have permission to invite '{g}' group", 403
    return True, None, None


def getCV(user_id):
    user = db_session.query(Users).filter(Users.id == user_id).one_or_none()
    cv = user.cv
    return cv


def getAcademicTranscript(user_id):
    user = db_session.query(Users).filter(Users.id == user_id).one_or_none()
    academicTranscript = user.academicRecord
    return academicTranscript


def updateCV(user_id, cv):
    user = db_session.query(Users).filter(Users.id == user_id).update(
        {"cv": cv}
    )
    db_session.commit()
    return user


def updateAcademicTranscript(user_id, academicTranscript):
    user = db_session.query(Users).filter(Users.id == user_id).update(
        {"academicRecord": academicTranscript}
    )
    db_session.commit()
    return user


def search_user(search: str):
    users = db_session.query(Users).filter(
        or_(Users.name.like("%" + search + "%"), Users.id.like("%" + search + "%"),
            Users.email.like("%" + search + "%"), Users.auid.like("%" + search + "%"))).all()
    return users


def send_invitation_email(email, name, userID, password):
    sender = current_app.config["EMAIL_ACCOUNT"]
    sender_pwd = current_app.config["EMAIL_PASSWORD"]
    smtp = smtplib.SMTP(current_app.config["EMAIL_SERVER_HOST"], current_app.config["EMAIL_SERVER_PORT"])
    # check the smtp is connected, delete the print later
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, sender_pwd)
    # Get EmailTemplate Path
    path = os.path.join(os.path.dirname(current_app.instance_path), "MTMS", "EmailTemplate")

    # Define msg root
    mes = MIMEMultipart('related')
    mes['From'] = current_app.config["EMAIL_SENDER_ADDRESS"]
    mes['To'] = Header(email, 'utf-8')
    mes['Subject'] = Header('Invites you to become Tutor & Marker', 'utf-8')

    # load html file
    html_path = os.path.join(path, "InvitationEmailTemplate.html")
    html_file = open(html_path, "r", encoding="utf-8")
    html = html_file.read()
    html_file.close()
    tmpl = Template(html)
    html = tmpl.render(name=name, userID=userID, password=password,
                       WebsiteLink=current_app.config["PROJECT_DOMAIN"])
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

    # smtp.quit()
    return True


def send_email_wrapper(ius, currentUser):
    from MTMS import db_session
    ius_email_status = []
    for ius_id in ius:
        i: InviteUserSaved = db_session.query(InviteUserSaved).filter(InviteUserSaved.id == ius_id).first()
        email_status: Email_Delivery_Status = create_email_sending_status(i.userID, EmailCategory.invite_user,
                                                                          i.email, currentUser, None)
        if email_status is None or not email_status[0]:
            return {"message": "Create email sending status error"}, 500
        ius_email_status.append((i, email_status[1]))
    for (i, email_status) in ius_email_status:
        password = generate_random_password()
        try:
            send_invitation_email(i.email, i.name, i.userID, password)
            user = Users(
                email=i.email,
                name=i.name,
                id=i.userID,
                password=password,
            )
            user.groups = i.Groups
            db_session.add(user)
            db_session.delete(i)
            db_session.commit()
            email_status.status = EmailStatus.sent
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            try:
                email_status.status = EmailStatus.failed
                email_status.error_message = str(e)
                db_session.commit()
            except Exception as e:
                db_session.rollback()
            continue
    return {"message": "Success"}, 200
