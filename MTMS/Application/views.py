import datetime
import werkzeug
from flask import request
from flask_restful import reqparse, Resource
from typing import List

from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id, get_average_gpa, get_course_by_id
from ..Utils.enums import ApplicationStatus, ApplicationType
from MTMS.Utils import validator
from MTMS.Models.users import Users
from MTMS.Models.applications import Application, SavedProfile, CourseApplication
from MTMS.Models.courses import CourseUser, RoleInCourse
from MTMS.Auth.services import auth, get_permission_group, check_user_permission
from .services import get_student_application_list_by_id, get_application_by_id, \
    saved_student_profile, get_saved_student_profile, save_course_application, get_course_application, upload_file, \
    check_application_data, exist_termName, get_all_application_by_term, get_status_application_by_term, \
    get_application_by_course_id


class NewApplication(Resource):
    @auth.login_required(role=get_permission_group("NewApplication"))
    def get(self, termID, app_type):
        """
        create a new application for current user
        ---
        tags:
          - Application
        parameters:
            - in: path
              name: termID
              type: string
              required: true
            - in: path
              name: type
              type: string
              required: true
        responses:
            200:
              schema:
                properties:
                  application_id:
                    type: integer
        security:
          - APIKeyHeader: ['Authorization']
        """
        if not exist_termName(termID):
            return {"message": "Term does not exist"}, 404
        current_user = auth.current_user()
        application = Application(createdDateTime=datetime.datetime.now(), studentID=current_user.id, status="Unsubmit",
                                  term=termID, type=app_type)
        db_session.add(application)
        db_session.commit()
        db_session.refresh(application)
        return {"application_id": application.ApplicationID}, 200


class saveApplication(Resource):
    @auth.login_required
    def post(self, application_id):
        """
        save the application profile
        ---
        tags:
          - Application
        parameters:
          - name: application_id
            in: path
            required: true
            schema:
              type: string
          - in: body
            name: body
            required: true
            schema:
              properties:
                applicationPersonalDetail:
                  type: array
                course:
                  type: array
                  items:
                    properties:
                      courseID:
                        type: integer
                      hasLearned:
                        type: boolean
                      grade:
                        type: string
                      preExperience:
                        type: string
                      preference:
                        type: integer
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        parser = reqparse.RequestParser()
        args = parser.add_argument('applicationPersonalDetail', type=dict, location='json', required=False) \
            .add_argument('course', type=list, location='json', required=False) \
            .add_argument('fileURLCV', type=str, location='json', required=False) \
            .add_argument('fileURLAD', type=str, location='json', required=False) \
            .parse_args()

        application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        current_user = auth.current_user()
        EditAnyApplicationPermission = check_user_permission(current_user, "EditAnyApplication")
        if not EditAnyApplicationPermission and application.status != ApplicationStatus.Unsubmit:
            return {"message": "This application has been completed."}, 400

        if current_user.id == application.studentID or EditAnyApplicationPermission:
            processed = 0
            if args['applicationPersonalDetail'] is not None:
                if len(args['applicationPersonalDetail']) == 0:
                    return {"message": "Given 'applicationPersonalDetail' field, but did not give any student personal detail"}, 400
                saved_student_profile_res = saved_student_profile(application, args['applicationPersonalDetail'])
                if saved_student_profile_res[0]:
                    processed += 1
                else:
                    return {"message": saved_student_profile_res[1]}, saved_student_profile_res[2]
            if args['course'] is not None:
                response = save_course_application(application, args["course"])
                if response[0]:
                    processed += 1
                else:
                    return {"message": response[1]}, response[2]
            if isinstance(args['fileURLCV'], str) and args['fileURLCV']:
                fileURLCV = eval(args['fileURLCV'])
                response = upload_file(application, 'cv', fileURLCV['_value'])
                if response[0]:
                    processed += 1
                else:
                    return {"message": response[1]}, response[2]

            if isinstance(args['fileURLAD'], str) and args['fileURLAD']:
                fileURLAD = eval(args['fileURLAD'])
                response = upload_file(application, 'academicRecord', fileURLAD['_value'])
                if response[0]:
                    processed += 1
                else:
                    return {"message": response[1]}, response[2]
            if processed >= 1:
                return {"message": "Successful"}, 200
            else:
                return {"message": "Did not give any valid data"}, 400
        else:
            return {"message": "Unauthorized Access"}, 403

    @auth.login_required()
    def get(self, application_id):
        """
        get the saved application profile
        ---
        tags:
          - Application
        parameters:
          - name: application_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              properties:
                application:
                  type: object
                  properties:
        """
        application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        current_user = auth.current_user()
        if current_user.id == application.studentID:
            saved_PersonalDetail = get_saved_student_profile(application)
            saved_course = get_course_application(application)
            return {"applicationPersonalDetail": saved_PersonalDetail, "course": saved_course}, 200
        else:
            return {"message": "Unauthorized Access"}, 403


class submitApplication(Resource):
    @auth.login_required()
    def get(self, application_id):
        application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        check = check_application_data(application)
        if not check[0]:
            return {"message": check[1]}, 400

        user: Users = application.Users
        profile: SavedProfile = application.SavedProfile
        if user.email is None:
            user.email = profile.email
        if user.name is None:
            user.name = profile.name
        if user.auid is None:
            user.auid = profile.auid
        if user.upi is None:
            user.upi = profile.upi

        user.currentlyOverseas = profile.currentlyOverseas
        user.willBackToNZ = profile.willBackToNZ
        user.isCitizenOrPR = profile.isCitizenOrPR
        user.haveValidVisa = profile.haveValidVisa
        user.enrolDetails = profile.enrolDetails
        user.studentDegree = profile.studentDegree
        user.haveOtherContracts = profile.haveOtherContracts
        user.otherContracts = profile.otherContracts
        user.maximumWorkingHours = profile.maximumWorkingHours
        user.cv = profile.cv
        user.academicRecord = profile.academicRecord

        application.status = ApplicationStatus.Pending.name
        application.submittedDateTime = datetime.datetime.now()
        db_session.commit()
        return {"message": "Success"}, 200


class Application_api(Resource):
    @auth.login_required()
    def delete(self, application_id):
        """
        delete the student application
        ---
        tags:
          - Application
        parameters:
          - name: application_id
            in: path
            required: true
            schema:
              type: integer
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        current_user: Users = auth.current_user()
        application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        if current_user.id == application.studentID or check_user_permission(current_user, "EditAnyApplication"):
            if application.status != ApplicationStatus.Unsubmit:
                return {"message": "Submitted application cannot be deleted."}, 400
            db_session.delete(application)
            db_session.commit()
            return {"message": "Successful"}, 200
        else:
            return {"message": "Unauthorized Access"}, 403

    @auth.login_required()
    def get(self, application_id):
        """
        get the student application meta information by id
        ---
        tags:
          - Application
        parameters:
          - name: application_id
            in: path
            required: true
            schema:
              type: integer
        responses:
          200:
            schema:
              properties:
                application:
                  type: object
                  properties:
        security:
          - APIKeyHeader: ['Authorization']
        """
        current_user: Users = auth.current_user()
        application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        if current_user.id == application.studentID or check_user_permission(current_user, "EditAnyApplication"):
            return application.serialize(), 200
        else:
            return {"message": "Unauthorized Access"}, 403


class ApplicationListByTerm(Resource):
    @auth.login_required(role=get_permission_group("ApplicationApproval"))
    def get(self, term_id, status, app_type):
        """
        get all applications by term (Approval)
        ---
        tags:
          - Application
        parameters:
          - name: term_id
            in: path
            required: true
            schema:
              type: integer
          - name: status
            in: path
            required: true
            schema:
              type: string
          - name: app_type
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              properties:
                application:
                  type: array
                  items:
                    type: object
                    properties:
        security:
          - APIKeyHeader: ['Authorization']
        """
        status = status[0].upper() + status[1:].lower()
        app_type = app_type.lower()
        if app_type not in [a.value for a in ApplicationType]:
            return {"message": "Invalid type. It should be tutor or marker"}, 400
        if not exist_termName(term_id):
            return {"message": "Term does not exist."}, 404
        if status == "All":
            res = get_all_application_by_term(term_id, app_type)
            if res[0]:
                applications = res[1]
        elif status == "Published":
            applications = get_status_application_by_term(term_id, "", True, app_type)
        elif status in [a.name for a in ApplicationStatus]:
            applications: list[Application] = get_status_application_by_term(term_id, status, False, app_type)
        else:
            return {"message": "Invalid status"}, 400
        response = []
        for a in applications:
            application_dict = a.serialize()
            if a.SavedProfile is not None:
                application_dict.update(a.SavedProfile.serialize())
            if a.Courses:
                application_dict.update({"PreferCourse": [c.serialize() for c in a.Courses]})
                preferCourseGPA = get_average_gpa([c.grade for c in a.Courses])
                application_dict.update({"PreferCourseGPA": preferCourseGPA})
                application_dict.update({"EnrolledCourse": [cu.serialize_with_course_information() for cu in a.course_users]})
            response.append(application_dict)
        return response, 200


class CurrentStudentApplicationList(Resource):
    @auth.login_required()
    def get(self):
        """
        get current student application list
        ---
        tags:
          - Application
        responses:
          200:
            schema:
              type: array
              items:
                type: object
                properties:
                  applicationID:
                    type: integer
                  createdDateTime:
                    type: string
                    format: date-time
                  submittedDateTime:
                    type: string
                    format: date-time
                  isCompleted:
                    type: boolean
        security:
          - APIKeyHeader: ['Authorization']
        """
        current_user = auth.current_user()
        if current_user is None:
            return {"message": "This student could not be found."}, 404

        return get_student_application_list_by_id(current_user.id), 200


class StudentApplicationList(Resource):
    @auth.login_required()
    def get(self, student_id):
        """
        get the student application list
        ---
        tags:
          - Application
        parameters:
          - name: student_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              type: array
              items:
                type: object
                properties:
                  applicationID:
                    type: integer
                  createdDateTime:
                    type: string
                    format: date-time
                  submittedDateTime:
                    type: string
                    format: date-time
                  isCompleted:
                    type: boolean
        security:
          - APIKeyHeader: ['Authorization']
        """
        if get_user_by_id(student_id) is None:
            return {"message": "This student could not be found."}, 404

        current_user: Users = auth.current_user()
        if current_user.id == student_id or check_user_permission(current_user, "GetEveryStudentProfile"):
            return get_student_application_list_by_id(student_id), 200
        else:
            return {"message": "Unauthorized Access"}, 403


class ApplicationApproval(Resource):
    @auth.login_required(role=get_permission_group("EditAnyApplication"))
    def put(self, application_id, status):
        """
        update the application status
        ---
        tags:
          - Application
        parameters:
          - name: application_id
            in: path
            required: true
            schema:
              type: integer
          - name: status
            in: path
            required: true
            schema:
              type: string
          - in: body
            name: body
            required: true
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        application: Application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        if application.type is None:
            return {"message": "Application Type Error! It may be due to an abnormal way of submitting the application."}, 400
        status = status[0].upper() + status[1:].lower()
        if status == "Accepted":
            args = request.json
            if not isinstance(args, list):
                return {"message": "Invalid input"}, 400
            if args is None:
                return {"message": "Missing required fields."}, 400
            if len(args) == 0:
                return {"message": "You must enroll for at least one course."}, 400
            for a in args:
                if 'courseID' not in a:
                    db_session.rollback()
                    return {"message": "You must select courses in all rows."}, 400
                course = get_course_by_id(a["courseID"])
                if course is None:
                    db_session.rollback()
                    return {"message": "Course does not exist."}, 404
                role: RoleInCourse = db_session.query(RoleInCourse).filter(
                    RoleInCourse.Name == application.type.value).one_or_none()
                if role is None:
                    db_session.rollback()
                    return {"message": "Role does not exist."}, 404
                if role.Name == "courseCoordinator":
                    db_session.rollback()
                    return {"message": "The application type is courseCoordinator."}, 400
                courseUserChecker: CourseUser = db_session.query(CourseUser).filter(
                    CourseUser.courseID == a['courseID'],
                    CourseUser.userID == application.studentID,
                    CourseUser.roleID == role.roleID).one_or_none()
                if courseUserChecker is not None:
                    db_session.rollback()
                    if courseUserChecker.isPublished:
                        return {
                                   "message": f"This student has already been enrolled to {course.courseNum}. Already published."}, 400
                    else:
                        return {
                                   "message": f"This student has already been enrolled to {course.courseNum}. Not published."}, 400
                courseUser = CourseUser(
                    courseID=a["courseID"],
                    userID=application.studentID,
                    roleID=role.roleID,
                    estimatedHours=a["estimatedHours"] if "estimatedHours" in a else None,
                    ApplicationID=application_id
                )
                db_session.add(courseUser)
            application.status = ApplicationStatus.Accepted
            db_session.commit()
            return {"message": "Application Accepted(No Published)"}, 200
        elif status == "Rejected":
            for cu in application.course_users:
                db_session.delete(cu)
            application.status = ApplicationStatus.Rejected
            db_session.commit()
            return {"message": "Application Rejected"}, 200
        if status not in [a.name for a in ApplicationStatus]:
            return {"message": "Invalid status"}, 400
        application.status = status
        db_session.commit()
        return {"message": "Successful"}, 200


class MultiApplicationStatus_api(Resource):
    @auth.login_required(role=get_permission_group("EditAnyApplication"))
    def put(self):
        """
        update multi application status
        ---
        tags:
          - Application
        parameters:
          - in: body
            name: body
            required: true
            type: array
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        response = request.json
        for r in response:
            application = get_application_by_id(r["applicationID"])
            if application is None:
                db_session.rollback()
                return {"message": "This application could not be found."}, 404
            status = r["status"][0].upper() + r["status"][1:].lower()
            if status not in [a.name for a in ApplicationStatus]:
                db_session.rollback()
                return {"message": "Invalid status"}, 400
            application.status = status
        db_session.commit()
        return {"message": "Successful"}, 200


class GetNumOfApplicationStatus(Resource):
    @auth.login_required(role=get_permission_group("EditAnyApplication"))
    def get(self, term_id, app_type):
        """
        get the number of each application status
        ---
        tags:
          - Application
        parameters:
            - name: term_id
              in: path
              required: true
              schema:
                type: integer
        responses:
          200:
            schema:
              properties:
                numberOfApplication:
                  type: integer
        security:
          - APIKeyHeader: ['Authorization']
        """
        if not exist_termName(term_id):
            return f"termID:{term_id} does not exist", 404
        result = {"accepted": 0, "rejected": 0, "pending": 0, "published": 0}
        for k in result:
            if k == "published":
                res = get_status_application_by_term(term_id, k, True, app_type)
            else:
                res = get_status_application_by_term(term_id, k, False, app_type)
            result[k] = len(res)
        result.update({"unpublished": result["accepted"] + result["rejected"]})
        print(result)
        return result, 200


class GetApplicationByCourseID(Resource):
    @auth.login_required
    def get(self, course_id):
        """
        get the application list by course id
        ---
        tags:
          - Application
        parameters:
            - name: course_id
              in: path
              required: true
              schema:
                type: integer
        responses:
          200:
            schema:
              properties:
                applicationList:
                  type: array
                  items:
                    type: object
                    properties:
                      applicationID:
                        type: integer
                      studentID:
                        type: integer
                      studentName:
                        type: string
                      status:
                        type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        if get_course_by_id(course_id) is None:
            return f"courseID:{course_id} does not exist", 404
        applications: list[Application] = get_application_by_course_id(course_id)
        return [a.serialize_application_detail() for a in applications], 200


class EndorsedApplicationByCC(Resource):
    @auth.login_required
    def get(self, applicationID, courseID):
        """
        endorsed or cancel endorsed application by course coordinator
        ---
        tags:
          - Application
        parameters:
            - name: applicationID
              in: path
              required: true
              schema:
                type: integer
            - name: courseID
              in: path
              required: true
              schema:
                type: integer
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        application: Application = get_application_by_id(applicationID)
        if application is None:
            return {"message": "This application could not be found."}, 404
        if application.type is None:
            return {
                       "message": "Application Type Error!  It may be due to an abnormal way of submitting the application."}, 400
        if application.status == ApplicationStatus.Unsubmit:
            return {"message": "The application has not been submitted yet."}, 400
        course = get_course_by_id(courseID)
        if course is None:
            return {"message": "This course could not be found."}, 404
        courseUserChecker: CourseUser = db_session.query(CourseUser).join(RoleInCourse).filter(
            CourseUser.courseID == courseID,
            CourseUser.userID == application.studentID,
            RoleInCourse.Name == application.type.name).one_or_none()
        if courseUserChecker is not None:
            if courseUserChecker.isPublished:
                return {
                           "message": f"This student has already been enrolled to {course.courseNum}. Already published."}, 400
        courseApplication: CourseApplication = db_session.query(CourseApplication).filter(
            CourseApplication.ApplicationID == applicationID,
            CourseApplication.courseID == courseID).one_or_none()
        if courseApplication is None:
            return {"message": "The student did not apply for this course"}, 404
        if courseApplication.courseCoordinatorEndorsed:
            courseApplication.courseCoordinatorEndorsed = False
            db_session.commit()
            return {"message": "Cancel Endorsed"}, 200
        courseApplication.courseCoordinatorEndorsed = True
        db_session.commit()
        return {"message": "Endorse Successfully!"}, 200


class PublishApplication(Resource):
    @auth.login_required
    def post(self):
        """
         Publish Applications
         ---
         tags:
           - Application
        """
        args = request.json
        if not isinstance(args, list):
            return {"message": "JSON format error"}, 400
        if len(args) == 0:
            return {"message": "No application selected"}, 400
        for a in args:
            application = get_application_by_id(a)
            if application is None:
                db_session.rollback()
                return {"message": f"ApplicationID:{a} could not be found."}, 404
            if application.isResultPublished:
                db_session.rollback()
                return {"message": f"ApplicationID:{a} has already been published."}, 400
            if application.status not in [ApplicationStatus.Accepted, ApplicationStatus.Rejected]:
                db_session.rollback()
                return {"message": f"The status of ApplicationID:{a} is neither accepted nor rejected"}, 400
            courseUsers: List[CourseUser] = application.course_users
            for cu in courseUsers:
                cu.isPublished = True
            application.isResultPublished = True
        db_session.commit()
        return {"message": "Successful"}, 200


def register(app):
    '''
        restful router.
        eg /api/auth/users
    '''
    register_api_blueprints(app, "Application", __name__,
                            [
                                (NewApplication, "/api/newApplication/<int:termID>/<string:app_type>"),
                                (StudentApplicationList, "/api/studentApplicationList/<string:student_id>"),
                                (CurrentStudentApplicationList, "/api/currentStudentApplicationList"),
                                (Application_api, "/api/application/<int:application_id>"),
                                (saveApplication, "/api/saveApplication/<int:application_id>"),
                                (submitApplication, "/api/submitApplication/<int:application_id>"),
                                (ApplicationListByTerm,
                                 "/api/applicationListByTerm/<int:term_id>/<string:status>/<string:app_type>"),
                                (ApplicationApproval, "/api/applicationApproval/<int:application_id>/<string:status>"),
                                (MultiApplicationStatus_api, "/api/multiApplicationStatus"),
                                (GetNumOfApplicationStatus,
                                 "/api/getNumOfApplicationStatus/<int:term_id>/<string:app_type>"),
                                (GetApplicationByCourseID, "/api/getApplicationByCourseID/<int:course_id>"),
                                (EndorsedApplicationByCC,
                                 "/api/endorsedApplicationByCC/<int:applicationID>/<int:courseID>"),
                                (PublishApplication, "/api/publishApplication"),
                            ])
