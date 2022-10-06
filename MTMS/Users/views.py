from flask_restful import reqparse, Resource
from flask import request
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id, generate_random_password
from MTMS.Utils.validator import empty_or_email
from MTMS.Utils import validator
from MTMS.Models.users import Users, InviteUserSaved
from MTMS.Auth.services import auth, get_permission_group
from MTMS.Users.services import get_group_by_name, save_attr_ius, validate_ius, send_invitation_email, getCV, \
    getAcademicTranscript
import datetime


class InviteUserSaved_api(Resource):
    @auth.login_required
    def get(self):
        user: Users = auth.current_user()
        if user is None:
            return {'message': 'User not found'}, 404
        return [i.serialize() for i in user.InviteUserSaved], 200

    @auth.login_required
    def post(self):
        parse = request.json
        currentUser: Users = auth.current_user()
        print(parse)
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
            res = save_attr_ius(i, ius)
            if not res[0]:
                return {"message": res[1]}, res[2]
            db_session.add(ius)

        for i in parse['updateRecords']:
            ius = db_session.query(InviteUserSaved).filter(InviteUserSaved.index == i['index'],
                                                           InviteUserSaved.saver_user_id == currentUser.id).first()
            if not ius:
                return {"message": "Update Records Error: This row was not found"}, 404
            res = save_attr_ius(i, ius)
            if not res[0]:
                return {"message": res[1]}, res[2]

        for i in parse['removeRecords']:
            ius = db_session.query(InviteUserSaved).filter(InviteUserSaved.index == i['index'],
                                                           InviteUserSaved.saver_user_id == currentUser.id).first()
            if not ius:
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
        ius: list[InviteUserSaved] = db_session.query(InviteUserSaved).filter(
            InviteUserSaved.saver_user_id == currentUser.id).all()
        res = validate_ius(ius)
        if not res[0]:
            return {"message": res[1]}, res[2]
        for i in ius:
            password = generate_random_password()
            user = Users(
                email=i.email,
                name=i.name,
                id=i.userID,
                password=password,
            )
            user.groups = i.Groups
            db_session.add(user)
            send_invitation_email(i.email, i.name, i.userID, password)

        db_session.commit()
        return {"message": "Success"}, 200


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
              properties:
                email:
                  type: string
                  format: email
                name:
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
            .parse_args()
        if len(args) == 0:
            return {"message": "Did not give any user profile"}, 400
        else:
            processed = 0
            if args['email'] is not None and args['email'].strip() != "":
                user.email = args['email']
                processed += 1
            if args['name'] is not None and args['name'].strip() != "":
                user.name = args['name']
                processed += 1
            db_session.commit()
            if processed >= 1:
                return {"message": "Successful"}, 200
            else:
                return {"message": "Did not give any valid user profile"}, 400


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
              properties:
                email:
                  type: string
                  format: email
                name:
                  type: string
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
        if current_user.id == user_id or len(
                set([g.groupName for g in current_user.groups]) & set(
                    get_permission_group("ChangeEveryUserProfile"))) > 0:
            parser = reqparse.RequestParser()
            args = parser.add_argument('email', type=empty_or_email, location='json', required=False) \
                .add_argument('name', type=str, location='json', required=False) \
                .parse_args()
            if len(args) == 0:
                return {"message": "Did not give any user profile"}, 400
            else:
                processed = 0
                if args['email'] is not None and args['email'].strip() != "":
                    user.email = args['email']
                    processed += 1
                if args['name'] is not None and args['name'].strip() != "":
                    user.name = args['name']
                    processed += 1
                db_session.commit()
                if processed >= 1:
                    return {"message": "Successful"}, 200
                else:
                    return {"message": "Did not give any valid user profile"}, 400
        else:
            return "Unauthorized Access", 403
class ManageUserFile(Resource):
    '''
    用于管理 user 的 cv ， academic transcript 等文件
    '''
    def get(self, user_id):
        cv = getCV(user_id)
        AcademicTranscript = getAcademicTranscript(user_id)

        return {"cv": cv, "AcademicTranscript": AcademicTranscript}, 200

class GetCV(Resource):
    '''
    用于获取 user 的 cv
    '''
    def get(self, user_id):
        return  {"cv": getCV(user_id)}, 200


class GetAcademicTranscript(Resource):
    '''
    用于获取 user 的 academic transcript
    '''
    def get(self, user_id):

        return { "AcademicTranscript": getAcademicTranscript(user_id)}, 200

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
                            ])
