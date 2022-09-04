from MTMS.model import Users, Groups, PersonalDetailSetting, StudentProfile
from MTMS import db_session


def get_student_profile_now_by_id(student_id):
    profile_id_list = db_session.query(PersonalDetailSetting.profileID, PersonalDetailSetting.name).all()
    result_dict = {}
    for p in profile_id_list:
        result_dict[p[1]] = db_session.query(StudentProfile).filter(StudentProfile.studentID == student_id, StudentProfile.profileID == p[0]).order_by(StudentProfile.dateTime.desc()).first()
    return result_dict

# def change_student_profile(student_id, ch):