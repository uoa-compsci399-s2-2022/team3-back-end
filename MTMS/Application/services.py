from MTMS.Models.applications import Application, CourseApplication, SavedProfile
from MTMS.Models.courses import Course, Term
from MTMS.Models.users import Users
from MTMS.Utils.validator import non_empty_string, email, is_email
from MTMS import db_session
import datetime
from MTMS.Utils.utils import get_user_by_id, filter_empty_value
from MTMS.Utils.enums import ApplicationStatus
from sqlalchemy import or_


def get_student_application_list_by_id(student_id):
    application_list: list[Application] = db_session.query(Application).filter(Application.studentID == student_id).all()
    result = []
    for application in application_list:
        a_dict = application.serialize()
        if not application.isResultPublished and application.status != ApplicationStatus.Unsubmit:
            a_dict["status"] = "Pending"
        result.append(a_dict)
    return result


def get_application_by_id(application_id):
    application = db_session.query(Application).filter(Application.ApplicationID == application_id).one_or_none()
    return application


def get_course_by_id(courseID):
    return db_session.query(Course).filter(Course.courseID == courseID).one_or_none()


def delete_course_application(application):
    try:
        for course in application.Courses:
            db_session.delete(course)
        return True
    except:
        db_session.rollback()
        return False


def save_course_application(application, args):
    delete_course_application(application)
    for c in args:
        c = filter_empty_value(c)
        lower_temp_c = {}
        for k in c:
            lower_temp_c[k.lower()] = c[k]
        course = get_course_by_id(lower_temp_c["courseid"])
        if course is None:
            return False, f"courseID:{lower_temp_c['courseid']} does not exist", 404
        courseApplication = db_session.query(CourseApplication).filter(
            CourseApplication.ApplicationID == application.ApplicationID,
            CourseApplication.courseID == lower_temp_c['courseid']).one_or_none()
        if not courseApplication:
            courseApplication = CourseApplication(courseID=lower_temp_c['courseid'],
                                                  ApplicationID=application.ApplicationID)

        courseApplication.hasLearned = lower_temp_c.get("haslearned")
        courseApplication.preExperience = lower_temp_c.get("preexperience")
        courseApplication.preference = lower_temp_c.get("preference")
        if lower_temp_c["haslearned"] == True:
            courseApplication.grade = lower_temp_c.get("grade")
        else:
            courseApplication.explanation = lower_temp_c.get("explanation")
        db_session.add(courseApplication)
    db_session.commit()
    return (True,)


def get_course_application(application: Application):
    courseApplications = application.Courses
    return [c.serialize() for c in courseApplications]


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
    applicationPersonalDetail = filter_empty_value(applicationPersonalDetail)
    for k in applicationPersonalDetail:
        if k == "studentDegree" and applicationPersonalDetail[k] is None:
            continue
        try:
            getattr(profile, k)
            setattr(profile, k, applicationPersonalDetail[k])
        except AttributeError:
            db_session.rollback()
            return False, f"Invalid field name: {k}", 400
        except ValueError as e:
            db_session.rollback()
            return False, str(e), 400
    db_session.commit()
    return True, None, None


def upload_file(application, key, value):
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

    # try:
    if hasattr(profile, key):
        setattr(profile, key, value)
    # except:
    #     db_session.rollback()
    #     return False, f"File Error", 400
    db_session.commit()
    return True, None, None


def check_application_data(application):
    profile: SavedProfile = application.SavedProfile
    if profile is None:
        return False, ["Did not save any application data"]
    user: Users = application.Users
    error_list = []
    id_attribute = ["name", "email", "upi", "auid"]
    profile_attribute = ["currentlyOverseas", "willBackToNZ",
                         "isCitizenOrPR", "haveValidVisa", "enrolDetails", "studentDegree",
                         "haveOtherContracts", "otherContracts", "maximumWorkingHours", "academicRecord",
                         "cv"]
    for i in id_attribute:
        if i == "email":
            if user.email is None and not is_email(profile.email):
                error_list.append(f"Please input correct Email")

        if not getattr(user, i) and not getattr(profile, i):
            error_list.append(f"Please input {i}")

    for i in profile_attribute:
        if isinstance(getattr(profile, i), str) and getattr(profile, i).strip() == "":
            setattr(profile, i, None)

        if i == "willBackToNZ" and profile.willBackToNZ is None:
            if profile.currentlyOverseas:
                error_list.append(f"Please input {i}")
            continue

        if i == "haveValidVisa" and profile.haveValidVisa is None:
            if not profile.isCitizenOrPR:
                error_list.append(f"Please input {i}")
            continue

        if i == "otherContracts" and profile.otherContracts is None:
            if profile.haveOtherContracts:
                error_list.append(f"Please input {i}")
            continue

        if i == "academicRecord" and profile.academicRecord is None:
            error_list.append(f"Please upload Transcript")
            continue

        if i == "cv" and profile.academicRecord is None:
            error_list.append(f"Please upload CV")
            continue

        if getattr(profile, i) is None or getattr(profile, i) is None:
            error_list.append(f"Please input {i}")


    if len(error_list) == 0:
        return True, []
    else:
        return False, error_list


def get_saved_student_profile(application):
    profile: SavedProfile = application.SavedProfile
    if profile is None:
        return None
    return profile.serialize()


def exist_termName(termID):
    if db_session.query(Term).filter(Term.termID == termID).one_or_none() is None:
        return False
    return True


def get_all_application_by_term(termID, app_type):
    if not exist_termName(termID):
        return False, f"termID:{termID} does not exist", 404
    applications = db_session.query(Application).join(Term).filter(
        Term.termID == termID, Application.type == app_type).all()
    return True, applications


def get_status_application_by_term(termID, status, isPublished, app_type):
    if status != "":
        status = status[0].upper() + status[1:].lower()
    if not exist_termName(termID):
        return False, f"termID:{termID} does not exist", 404
    if not isPublished:
        applications = db_session.query(Application).join(Term).filter(
            Term.termID == termID, Application.status == status,
            or_(Application.isResultPublished == False, Application.isResultPublished == None),
            Application.type == app_type).all()
    else:
        applications = db_session.query(Application).join(Term).filter(
            Term.termID == termID, Application.isResultPublished == True,
            Application.type == app_type).all()
    return applications


def get_application_by_course_id(courseID):
    applications = db_session.query(Application).join(CourseApplication).filter(
        CourseApplication.courseID == courseID).all()
    return applications
