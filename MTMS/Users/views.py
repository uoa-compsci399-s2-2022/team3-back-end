from flask_restful import reqparse, Resource
from flask import request, current_app
from MTMS import db_session, cache
from MTMS.Models.setting import Email_Delivery_Status
from MTMS.Utils.enums import EmailCategory, EmailStatus
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id, generate_random_password, \
    create_email_sending_status
from MTMS.Utils.validator import empty_or_email
from MTMS.Utils import validator
from MTMS.Models.users import Users, InviteUserSaved
from MTMS.Auth.services import auth, get_permission_group, check_user_permission
from MTMS.Users.services import get_group_by_name, save_attr_ius, validate_ius, getCV, \
    getAcademicTranscript, change_user_profile, updateCV, updateAcademicTranscript, search_user, send_email_wrapper

import datetime
from celery.result import AsyncResult


class InviteUserSaved_api(Resource):
    @auth.login_required(role=get_permission_group("InviteStudent"))
    def get(self):
        """
        get invite user saved
        ---
        tags:
          - Users
        responses:
          200:
            schema:
              message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        user: Users = auth.current_user()
        if user is None:
            return {'message': 'User not found'}, 404
        return [i.serialize() for i in user.InviteUserSaved], 200

    @auth.login_required(role=get_permission_group("InviteStudent"))
    def post(self):
        """
        save invite user edit info
        ---
        tags:
            - Users
        parameters:
            - name: body
              in: body
              required: true
              schema:
                    properties:
                        insertRecords:
                            type: array
                            items:
                                type: object
                        updateRecords:
                            type: array
                            items:
                                type: object
        security:
          - APIKeyHeader: ['Authorization']
        """
        parse = request.json
        currentUser: Users = auth.current_user()
        if not parse:
            return {"message": "No data provided"}, 400

        if 'insertRecords' not in parse or 'updateRecords' not in parse or 'removeRecords' not in parse:
            return {"message": "Json format error"}, 400

        for i in parse['insertRecords']:
            iusInDB = db_session.query(InviteUserSaved).filter(InviteUserSaved.saver_user_id == currentUser.id,
                                                               InviteUserSaved.index == i['index']).first()
            if iusInDB:
                db_session.rollback()
                return {"message": "The index already exists"}, 400

            ius = InviteUserSaved(
                saver_user_id=currentUser.id,
                index=i['index']
            )
            res = save_attr_ius(i, ius, currentUser)
            if not res[0]:
                return {"message": res[1]}, res[2]
            db_session.add(ius)

        for i in parse['updateRecords']:
            ius = db_session.query(InviteUserSaved).filter(InviteUserSaved.index == i['index'],
                                                           InviteUserSaved.saver_user_id == currentUser.id).first()
            if not ius:
                db_session.rollback()
                return {"message": "Update Records Error: This row was not found"}, 404
            res = save_attr_ius(i, ius, currentUser)
            if not res[0]:
                return {"message": res[1]}, res[2]

        for i in parse['removeRecords']:
            ius = db_session.query(InviteUserSaved).filter(InviteUserSaved.index == i['index'],
                                                           InviteUserSaved.saver_user_id == currentUser.id).first()
            if not ius:
                db_session.rollback()
                return {"message": "Delete Records Error: This row was not found"}, 404
            db_session.delete(ius)

        db_session.commit()
        return {"message": "Success"}, 200


class InviteUser(Resource):
    @auth.login_required()
    def get(self):
        """
        invite user to join MTMS
        ---
        tags:
          - Users
        responses:
          200:
            schema:
              message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        currentUser: Users = auth.current_user()
        if currentUser is None:
            return {'message': 'User not found'}, 404
        if len([email for email in currentUser.SenderEmailDeliveryStatus if email.status == EmailStatus.sending]) > 0:
            return {'message': 'You are sending email now. Please check Sending Status page.'}, 400
        ius: list[InviteUserSaved] = db_session.query(InviteUserSaved).filter(
            InviteUserSaved.saver_user_id == currentUser.id).all()
        res = validate_ius(ius, currentUser)
        if not res[0]:
            return {"message": res[1]}, res[2]

        if current_app.config['CELERY_BROKER_URL'].strip():
            from MTMS.tasks import send_email_celery
            task: AsyncResult = send_email_celery.delay([i.id for i in ius], currentUser.id)
            result = task.wait()
            return res[0], res[1]
        else:
            res = send_email_wrapper([i.id for i in ius], currentUser.id)
            return res[0], res[1]


class CurrentUserProfile(Resource):
    @auth.login_required()
    def get(self):
        """
        get current user profile
        ---
        tags:
          - Users
        responses:
          200:
            schema:
        security:
          - APIKeyHeader: ['Authorization']
        """
        users = auth.current_user()
        if users is None:
            return {"message": "This user could not be found."}, 404
        return users.profile_serialize(), 200

    @auth.login_required()
    def put(self):
        """
        change current user profile
        ---
        tags:
          - Users
        parameters:
          - in: body
            name: body
            required: true
            schema:
              id: changeUserProfileSchema
              properties:
                email:
                  type: string
                  format: email
                name:
                  type: string
                upi:
                    type: string
                auid:
                    type: integer
                enrolDetails:
                    type: string
                studentDegree:
                    type: string
        responses:
          200:
            schema:
              message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        user: Users = auth.current_user()
        if user is None:
            return {"message": "This user could not be found."}, 404
        parser = reqparse.RequestParser()
        args = parser.add_argument('email', type=empty_or_email, location='json', required=False) \
            .add_argument('name', type=str, location='json', required=False) \
            .add_argument('upi', type=str, location='json', required=False) \
            .add_argument('auid', type=int, location='json', required=False) \
            .add_argument('enrolDetails', type=str, location='json', required=False) \
            .add_argument('studentDegree', type=str, location='json', required=False) \
            .parse_args()
        if len(args) == 0:
            return {"message": "Did not give any user profile"}, 400
        else:
            res = change_user_profile(user, args)
            if res[0]:
                return {"status": 1, "message": "Success"}, 200
            else:
                return {"status": 0, "message": res[1]}, res[2]


class UserProfile(Resource):
    @auth.login_required()
    def get(self, user_id):
        """
        get user profile
        ---
        tags:
          - Users
        parameters:
          - name: user_id
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
        users = get_user_by_id(user_id)
        if users is None:
            return {"message": "This user could not be found."}, 404
        return users.profile_serialize(), 200

    @auth.login_required()
    def put(self, user_id):
        """
        change the user profile
        ---
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            required: true
            schema:
              type: string
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/changeUserProfileSchema'
        responses:
          200:
            schema:
              message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        user: Users = get_user_by_id(user_id)
        if user is None:
            return {"message": "This user could not be found."}, 404

        current_user: Users = auth.current_user()
        if current_user.id == user_id or check_user_permission(current_user, "ChangeEveryUserProfile"):
            parser = reqparse.RequestParser()
            args = parser.add_argument('email', type=empty_or_email, location='json', required=False) \
                .add_argument('name', type=str, location='json', required=False) \
                .add_argument('upi', type=str, location='json', required=False) \
                .add_argument('auid', type=int, location='json', required=False) \
                .add_argument('enrolDetails', type=str, location='json', required=False) \
                .add_argument('studentDegree', type=str, location='json', required=False) \
                .parse_args()
            if len(args) == 0:
                return {"message": "Did not give any user profile"}, 400
            else:
                res = change_user_profile(user, args)
                if res[0]:
                    return {"status": 1, "message": "Success"}, 200
                else:
                    return {"status": 0, "message": res[1]}, res[2]
        else:
            return "Unauthorized Access", 403


class ManageUserFile(Resource):
    def get(self, user_id):
        '''
            用于管理 user 的 cv ， academic transcript 等文件
            tags:
              - Users
            parameters:
              - name: user_id
                in: path
                required: true
                schema:
                  type: string
            responses:
              200:
                schema:
                  message:
                      type: string
            '''
        cv = getCV(user_id)
        AcademicTranscript = getAcademicTranscript(user_id)

        return {"cv": cv, "AcademicTranscript": AcademicTranscript}, 200


class GetCV(Resource):
    '''
    用于获取 user 的 cv
    '''

    def get(self, user_id):
        '''
        用于获取 user 的 cv
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              message:
                  type: string
        '''
        return {"cv": getCV(user_id)}, 200

    def post(self, user_id):
        '''
        用于上传 user 的 cv
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              message:
                  type: string
        '''
        parser = reqparse.RequestParser()
        arg = parser.add_argument('cv', type=str, location='json', required=True).parse_args()
        cv = arg['cv']
        user = updateCV(user_id, cv)
        return {'mes': 'success'}, 200


class GetAcademicTranscript(Resource):
    '''
    用于获取 user 的 academic transcript
    '''

    def get(self, user_id):
        '''
        用于获取 user 的 academic transcript
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              message:
                  type: string
        '''
        return {"AcademicTranscript": getAcademicTranscript(user_id)}, 200

    def post(self, user_id):
        '''
        用于上传 user 的 academic transcript
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              message:
                  type: string
        '''
        parser = reqparse.RequestParser()
        arg = parser.add_argument('AcademicTranscript', type=str, location='json', required=True).parse_args()
        AcademicTranscript = arg['AcademicTranscript']
        user = updateAcademicTranscript(user_id, AcademicTranscript)
        return {'mes': 'success'}, 200


class SearchUser(Resource):
    @auth.login_required()
    def get(self, search):
        """
        search user
        ---
        tags:
          - Users
        parameters:
          - name: search
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
        users = search_user(search)
        return [user.profile_serialize() for user in users], 200


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Users", __name__,
                            [
                                # (StudentPersonalDetail, "/api/StudentPersonalDetail/<string:student_id>"),
                                (CurrentUserProfile, "/api/currentUserProfile"),
                                (UserProfile, "/api/UserProfile/<string:user_id>"),
                                (InviteUser, "/api/inviteUser"),
                                (InviteUserSaved_api, "/api/inviteUserSaved"),
                                (ManageUserFile, "/api/manageUserFile/<string:user_id>"),
                                (GetCV, "/api/getCV/<string:user_id>"),
                                (GetAcademicTranscript, "/api/getAcademicTranscript/<string:user_id>"),
                                (SearchUser, "/api/searchUser/<string:search>"),
                            ])
