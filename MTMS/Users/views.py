import datetime
import json

from flask import request, jsonify
from flask_restful import reqparse, marshal_with, Resource, fields, marshal
from MTMS import db_session
from MTMS.utils import register_api_blueprints
from MTMS.model import Users, Groups, PersonalDetailSetting, StudentProfile
from MTMS.Auth.services import auth, get_permission_group
from .services import get_student_profile_now_by_id


class StudentProfile(Resource):
    @auth.login_required()
    def get(self, student_id):
        """
        get the student personal detail field
        ---
        tags:
          - Users
        parameters:
          - name: student_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
        security:
          - APIKeyHeader: ['Authorization']
        """
        return get_student_profile_now_by_id(student_id), 200

    def put(self, student_id):
        """
        change the student personal detail field
        ---
        tags:
          - Users
        parameters:
          - name: student_id
            in: path
            required: true
            schema:
              type: string
          - in: body
            name: body
            required: true
            schema:
              properties:
                fields:
                  type: array
                  items:
                    properties:
                      profileName:
                        type: string
                      value:
                        type: string
        responses:
          200:
            schema:
        security:
          - APIKeyHeader: ['Authorization']
        """
        parser = reqparse.RequestParser()
        args = parser.add_argument('fields', type=list, location='json', required=True, help="Did not change any user profile") \
            .parse_args()
        print(args)






def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Users", __name__,
                            [
                                (StudentProfile, "/api/StudentProfile/<string:student_id>"),
                            ])
