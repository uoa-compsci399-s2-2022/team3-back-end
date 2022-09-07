import datetime

from MTMS.Models.users import Users, PersonalDetailSetting, StudentProfile
from MTMS import db_session
from MTMS.Utils.utils import get_user_by_id


def get_student_profile_now_by_id(student_id):
    profile_id_list = db_session.query(PersonalDetailSetting.profileID, PersonalDetailSetting.name).all()
    result_dict = {}
    for p in profile_id_list:
        profile = db_session.query(StudentProfile.value)\
            .filter(StudentProfile.studentID == student_id,StudentProfile.profileID == p[0])\
            .order_by(StudentProfile.dateTime.desc()).first()
        if profile is None:
            result_dict[p[1]] = None
        else:
            result_dict[p[1]] = profile[0]
    return result_dict


def change_student_profile(student_id, profile_list):
    try:
        user: Users = get_user_by_id(student_id)
        for p in profile_list:
            profileField: PersonalDetailSetting = db_session.query(PersonalDetailSetting).filter(
                PersonalDetailSetting.name == p["profileName"]).one_or_none()
            profile = StudentProfile(
                dateTime=datetime.datetime.now(),
                profileID=profileField.profileID,
                value=p["value"]
            )
            user.StudentProfile.append(profile)
            db_session.commit()
        return True
    except:
        return False