from MTMS.Models.users import StudentProfile
<<<<<<< HEAD
from MTMS.Models.applications import Application, CourseApplication
from MTMS.Models.courses import Course
=======
from MTMS.Models.applications import Application
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> parent of 9471290 (add register function)
=======
>>>>>>> parent of 9471290 (add register function)
=======
>>>>>>> parent of 9471290 (add register function)
from MTMS.Utils.validator import non_empty_string
from MTMS import db_session

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
                return (False, f"courseID:{lower_temp_c['courseid']} does not exist", 404)
            courseApplication = db_session.query(CourseApplication).filter(CourseApplication.ApplicationID == application.ApplicationID, CourseApplication.courseID == lower_temp_c['courseid']).one_or_none()
            if courseApplication:
                return (False, "This course already exists in this application", 400)
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
        return (False, "Unexpected Error", 400)