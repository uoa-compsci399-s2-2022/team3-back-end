import datetime
import json

from MTMS.model import Users, Groups, PersonalDetailSetting, StudentProfile, Application
from MTMS import db_session
from MTMS.utils import get_user_by_id


def get_student_application_list_by_id(student_id):
    application_list = db_session.query(Application).filter(Application.studentID == student_id).all()
    return [a.serialize() for a in application_list]


def get_application_by_id(application_id):
    application = db_session.query(StudentProfile).filter(StudentProfile.applicationID == application_id).one_or_none()
    return application