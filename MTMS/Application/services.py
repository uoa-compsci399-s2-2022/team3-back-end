from MTMS.Models.applications import Application, CourseApplication, SavedProfile
from MTMS.Models.courses import Course
from MTMS.Models.users import Users
from MTMS.Utils.validator import non_empty_string
from MTMS import db_session
import datetime
from MTMS.Utils.utils import get_user_by_id


def get_student_application_list_by_id(student_id):
    application_list = db_session.query(Application).filter(Application.studentID == student_id).all()
    return [a.serialize() for a in application_list]


def get_application_by_id(application_id):
    application = db_session.query(Application).filter(Application.ApplicationID == application_id).one_or_none()
    return application


def get_course_by_id(courseID):
    return db_session.query(Course).filter(Course.courseID == courseID).one_or_none()


def add_course_application(application, args):
    try:
        for c in args:
            lower_temp_c = {}
            for k in c:
                lower_temp_c[k.lower()] = c[k]
            course = get_course_by_id(lower_temp_c["courseid"])
            if course is None:
                return False, f"courseID:{lower_temp_c['courseid']} does not exist", 404
            courseApplication = db_session.query(CourseApplication).filter(
                CourseApplication.ApplicationID == application.ApplicationID,
                CourseApplication.courseID == lower_temp_c['courseid']).one_or_none()
            if courseApplication:
                return False, "This course already exists in this application", 400
            if lower_temp_c["haslearned"] == True:
                new_courseApplication = CourseApplication(courseID=lower_temp_c['courseid'],
                                                          ApplicationID=application.ApplicationID,
                                                          hasLearned=lower_temp_c["haslearned"],
                                                          grade=lower_temp_c["grade"],
                                                          preExperience=lower_temp_c["preexperience"],
                                                          )
            else:
                new_courseApplication = CourseApplication(courseID=lower_temp_c['courseid'],
                                                          ApplicationID=application.ApplicationID,
                                                          hasLearned=lower_temp_c["haslearned"],
                                                          explanation=lower_temp_c["explanation"],
                                                          preExperience=lower_temp_c["preexperience"],
                                                          )
            db_session.add(new_courseApplication)
        db_session.commit()
        return (True,)
    except:
        return False, "Unexpected Error", 400


def saved_student_profile(application, applicationPersonalDetail):
    profile = application.SavedProfile
    if profile is None:
        profile = SavedProfile(
            applicationID=application.ApplicationID,
            savedTime=datetime.datetime.now(),
        )
        db_session.add(profile)
    else:
        profile.savedTime = datetime.datetime.now()
    user = get_user_by_id(application.studentID)
    if user is None:
        db_session.rollback()
        return False, "The user for this application does not exist", 404

    for k in applicationPersonalDetail:
        try:
            getattr(profile, k)
            setattr(profile, k, applicationPersonalDetail[k])
        except AttributeError:
            db_session.rollback()
            return False, f"Invalid field name: {k}", 400
        except ValueError as e:
            return False, str(e), 400
    db_session.commit()
    return True, None, None


def get_saved_student_profile(application):
    profile: SavedProfile = application.SavedProfile
    if profile is None:
        return None
    return profile.serialize()
