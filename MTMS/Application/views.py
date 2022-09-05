import datetime
import json

from flask import request, jsonify
from flask_restful import reqparse, marshal_with, Resource, fields, marshal
from MTMS import db_session
from MTMS.utils import register_api_blueprints, get_user_by_id, email, empty_or_email
from MTMS.model import Users, Groups, PersonalDetailSetting, StudentProfile, Application
from MTMS.Auth.services import auth, get_permission_group
from .services import get_student_application_list_by_id, get_application_by_id


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
                            ])