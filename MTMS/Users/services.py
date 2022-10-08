from MTMS.Models.users import Users, Groups, InviteUserSaved
from MTMS.Utils.validator import empty_or_email
import datetime
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import current_app
from MTMS import db_session, cache
from MTMS.Utils.utils import response_for_services, generate_validation_code, get_user_by_id, filter_empty_value, StudentDegreeEnum
import smtplib
import os
from jinja2 import Template

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


def save_attr_ius(i, ius):
    print(ius.index, i)
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
                continue
            ius.Groups = []
            for g in i[k]:
                group = get_group_by_name(g)
                if not group:
                    db_session.rollback()
                    return False, "Group not found", 404
                ius.Groups.append(group)
        else:
            if hasattr(ius, k):
                setattr(ius, k, i[k])
            else:
                db_session.rollback()
                return False, f"Update Records Error: The column '{k}' was not found", 404
    return True, None, None


def validate_ius(iusList):
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
            return False, "User ID already exists", 400

        if not i.name:
            return False, "Name is empty", 400

        if not i.Groups:
            return False, "Groups is empty", 400
    return True, None, None


def send_invitation_email(email, name, userID, password):
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
    mes['Subject'] = Header('Invites you to become Tutor & Marker', 'utf-8')

    # load html file
    html_path = os.path.join(path, "InvitationEmailTemplate.html")
    html_file = open(html_path, "r", encoding="utf-8")
    html = html_file.read()
    html_file.close()
    tmpl = Template(html)
    html = tmpl.render(name=name, userID=userID, password=password, WebsiteLink=current_app.config["PROJECT_DOMAIN"])
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


def getCV(user_id):
    user = db_session.query(Users).filter(Users.id == user_id).one_or_none()
    cv = user.cv
    return cv

def getAcademicTranscript(user_id):
    user = db_session.query(Users).filter(Users.id == user_id).one_or_none()
    academicTranscript = user.academicRecord
    return academicTranscript