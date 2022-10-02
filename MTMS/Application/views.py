import datetime

from flask_restful import reqparse, Resource
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id, ApplicationStatus
from MTMS.Utils import validator
from MTMS.Models.users import Users
from MTMS.Models.applications import Application
from MTMS.Auth.services import auth, get_permission_group
from .services import get_student_application_list_by_id, get_application_by_id, add_course_application, saved_student_profile, get_saved_student_profile

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
        current_user = auth.current_user()
        application = Application(createdDateTime=datetime.datetime.now(), studentID=current_user.id, status="Unsubmit", term=termID)
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
            .add_argument('course', type=validator.application_course_list, location='json', required=False) \
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
                    return {"message": "Given 'applicationPersonalDetail' field, but did not give any student personal detail"}, 400
                saved_student_profile_res = saved_student_profile(application, args['applicationPersonalDetail'])
                if saved_student_profile_res[0]:
                    processed += 1
                else:
                    return {"message": saved_student_profile_res[1]}, saved_student_profile_res[2]
            if args['course'] is not None:
                if len(args['course']) == 0:
                    return {"message": "Given 'course' field, Did not give any course information"}, 400
                response = add_course_application(application, args["course"])
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
            saved = get_saved_student_profile(application)
            if saved is None:
                return {"message": "No"}, 404
            else:
                return saved, 200
        else:
            return {"message": "Unauthorized Access"}, 403





# class submitApplication(Resource):
#     def get(self, application_id):


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
                set([g.groupName for g in current_user.groups]) & set(get_permission_group("GetEveryStudentProfile"))) > 0:
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
                                (Application_api, "/api/application/<string:application_id>"),
                                (saveApplication, "/api/saveApplication/<string:application_id>")
                            ])
