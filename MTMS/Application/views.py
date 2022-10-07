import datetime
import werkzeug
from flask import request
from flask_restful import reqparse, Resource
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id, ApplicationStatus
from MTMS.Utils import validator
from MTMS.Models.users import Users
from MTMS.Models.applications import Application, SavedProfile
from MTMS.Auth.services import auth, get_permission_group
from .services import get_student_application_list_by_id, get_application_by_id, \
    saved_student_profile, get_saved_student_profile, save_course_application, get_course_application, upload_file, \
    check_application_data, exist_termName, get_all_application_by_term, get_status_application_by_term


class NewApplication(Resource):
    @auth.login_required(role=get_permission_group("NewApplication"))
    def get(self, termID):
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
                                  term=termID)
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
        if application.status != ApplicationStatus.Unsubmit:
            return {"message": "This application has been completed."}, 400
        current_user = auth.current_user()
        if current_user.id == application.studentID or len(
                set([g.groupName for g in current_user.groups]) & set(get_permission_group("EditAnyApplication"))) > 0:
            processed = 0
            if args['applicationPersonalDetail'] is not None:
                if len(args['applicationPersonalDetail']) == 0:
                    return {
                               "message": "Given 'applicationPersonalDetail' field, but did not give any student personal detail"}, 400
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

        application.status = ApplicationStatus.Pending.name
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
        if current_user.id == application.studentID or len(
                set([g.groupName for g in current_user.groups]) & set(get_permission_group("EditAnyApplication"))) > 0:
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
        if current_user.id == application.studentID or len(
                set([g.groupName for g in current_user.groups]) & set(get_permission_group("EditAnyApplication"))) > 0:
            return application.serialize(), 200
        else:
            return {"message": "Unauthorized Access"}, 403


class ApplicationListByTerm(Resource):
    @auth.login_required(role=get_permission_group("ApplicationApproval"))
    def get(self, term_id, status):
        """
        get all applications by term
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
        status = status[0].upper() + status[1:]
        if not exist_termName(term_id):
            return {"message": "Term does not exist."}, 404
        if status == "all":
            applications = get_all_application_by_term(term_id)
        elif status in [a.name for a in ApplicationStatus]:
            applications: list[Application] = get_status_application_by_term(term_id, status)
        else:
            return {"message": "Invalid status"}, 400
        response = []
        for a in applications:
            application_dict = a.serialize()
            if a.SavedProfile is not None:
                application_dict.update(a.SavedProfile.serialize())
            if a.Courses:
                application_dict.update({"PreferCourse": [c.serialize() for c in a.Courses]})
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
        if current_user.id == student_id or len(
                set([g.groupName for g in current_user.groups]) & set(
                    get_permission_group("GetEveryStudentProfile"))) > 0:
            return get_student_application_list_by_id(student_id), 200
        else:
            return {"message": "Unauthorized Access"}, 403


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Application", __name__,
                            [
                                (NewApplication, "/api/newApplication/<int:termID>"),
                                (StudentApplicationList, "/api/studentApplicationList/<string:student_id>"),
                                (CurrentStudentApplicationList, "/api/currentStudentApplicationList"),
                                (Application_api, "/api/application/<int:application_id>"),
                                (saveApplication, "/api/saveApplication/<int:application_id>"),
                                (submitApplication, "/api/submitApplication/<int:application_id>"),
                                (ApplicationListByTerm, "/api/applicationListByTerm/<int:term_id>/<string:status>"),
                            ])
