from MTMS.Models.users import StudentProfile
from MTMS.Models.applications import Application
from MTMS.utils.validator import non_empty_string
from MTMS import db_session


def get_student_application_list_by_id(student_id):
    application_list = db_session.query(Application).filter(Application.studentID == student_id).all()
    return [a.serialize() for a in application_list]


def get_application_by_id(application_id):
    application = db_session.query(StudentProfile).filter(StudentProfile.applicationID == application_id).one_or_none()
    return application