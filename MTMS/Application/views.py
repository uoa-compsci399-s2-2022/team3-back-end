import datetime

from flask_restful import reqparse, Resource
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id
from MTMS.Models.users import Users
from MTMS.Models.applications import Application
from MTMS.Auth.services import auth, get_permission_group
from .services import get_student_application_list_by_id, get_application_by_id
from MTMS.Users.services import change_student_profile

class NewApplication(Resource):
    @auth.login_required(role=get_permission_group("NewApplication"))
    def get(self):
        """
        create a new application for current user
        ---
        tags:
          - Application
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
        application = Application(createdDateTime=datetime.datetime.now(), studentID=current_user.id, isCompleted=False)
        db_session.add(application)
        db_session.commit()
        db_session.refresh(application)
        return {"application_id": application.ApplicationID}, 200


class saveApplication(Resource):
    def post(self, application_id):
        """
        save the application
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
                studentPersonalDetail:
                  type: array
                  items:
                    properties:
                      profileName:
                        type: string
                      value:
                        type: string
                course:
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
        parser = reqparse.RequestParser()
        args = parser.add_argument('studentPersonalDetail', type=list, location='json', required=False) \
            .add_argument('course', type=list, location='json', required=False) \
            .parse_args()
        application = get_application_by_id(application_id)
        if application is None:
            return {"message": "This application could not be found."}, 404
        if application.isCompleted:
            return {"message": "This application has been completed."}, 400
        current_user = auth.current_user()
        if current_user.id == application.studentID or len(
                set(current_user.groups) & set(get_permission_group("EditAnyApplication"))) > 0:
            processed = 0
            if args['studentPersonalDetail'] is not None:
                if len(args['studentPersonalDetail']) == 0:
                    return {"message": "Did not give any student personal detail"}, 400
                if change_student_profile(application.studentID, args['studentPersonalDetail']):
                    processed += 1
                else:
                    return {"message": "Error"}, 400
            if args['course'] is not None:
                if len(args['course']) == 0:
                    return {"message": "Did not give any course information"}, 400
            db_session.commit()
            if processed >= 1:
                return {"message": "Successful"}, 200
            else:
                return {"message": "Did not give any valid information"}, 400
        else:
            return "Unauthorized Access", 403


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
                set(current_user.groups) & set(get_permission_group("EditAnyApplication"))) > 0:
            db_session.delete(application)
            db_session.commit()
            return {"message": "Successful"}, 200
        else:
            return "Unauthorized Access", 403


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
                set(current_user.groups) & set(get_permission_group("GetEveryStudentProfile"))) > 0:
            return get_student_application_list_by_id(student_id), 200
        else:
            return "Unauthorized Access", 403


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Application", __name__,
                            [
                                (NewApplication, "/api/newApplication"),
                                (StudentApplicationList, "/api/studentApplicationList/<string:student_id>"),
                                (Application_api, "/api/application/<string:application_id>"),
                                (saveApplication, "/api/saveApplication/<string:application_id>")
                            ])
