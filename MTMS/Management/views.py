from flask_restful import Resource, fields, marshal
from MTMS import db_session
from MTMS.utils.utils import register_api_blueprints
from MTMS.Models.users import Users, Groups, PersonalDetailSetting
from MTMS.Auth.services import auth, get_permission_group
from .services import get_user_by_id, get_group_by_name, add_group, delete_group


PersonalDetail_fields = {}
PersonalDetail_fields.update({'name': fields.String,
                         'Desc': fields.String,
                         'subProfile': fields.Nested(PersonalDetail_fields),
                         'visibleCondition': fields.String,
                         'type': fields.String,
                         'isMultiple': fields.Boolean,
                         'minimum': fields.Integer,
                         'maximum': fields.Integer,
                         'Options': fields.List(fields.String)})


class UserGroupManagement(Resource):
    @auth.login_required(role=get_permission_group("UserGroupManagement"))
    def post(self, userID, groupName):
        """
        add user to the group
        ---
        tags:
          - Management
        parameters:
          - name: userID
            in: path
            required: true
            schema:
              type: string
          - name: groupName
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        user: Users = get_user_by_id(userID)
        group: Groups = get_group_by_name(groupName)
        if not user or not group:
            return {"message": "This user or group could not be found."}, 404
        add_group(user, group)
        return {"message": "Successful"}, 200

    @auth.login_required(role=get_permission_group("UserGroupManagement"))
    def delete(self, userID, groupName):
        """
        delete user from the group
        ---
        tags:
          - Management
        parameters:
          - name: userID
            in: path
            required: true
            schema:
              type: string
          - name: groupName
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        user: Users = get_user_by_id(userID)
        group: Groups = get_group_by_name(groupName)
        if not user or not group:
            return {"message": "This user or group could not be found."}, 404
        delete_group(user, group)
        return {"message": "Successful"}, 200

    @auth.login_required(role=get_permission_group("UserGroupManagement"))
    def get(self, userID):
        """
        get the user group
        ---
        tags:
          - Management
        parameters:
          - name: userID
            in: path
            required: true
            schema:
              type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
                groups:
                  type: array
        security:
          - APIKeyHeader: ['Authorization']
        """
        user: Users = get_user_by_id(userID)
        if not user:
            return {"message": "This user could not be found."}, 404
        groupName = [g.groupName for g in user.groups]
        return {"message": "Successful", "groups": groupName}, 200


class PersonalDetail(Resource):
    @auth.login_required()
    def get(self):
        """
        get the student personal detail field
        ---
        tags:
          - Management
        responses:
          200:
            schema:
        security:
          - APIKeyHeader: ['Authorization']
        """
        allPersonalDetail = db_session.query(PersonalDetailSetting).filter(
            PersonalDetailSetting.superProfileID == None).all()
        response = [marshal(p.serialize(), PersonalDetail_fields) for p in allPersonalDetail]
        return response, 200


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Management", __name__,
                            [(UserGroupManagement, "/api/userGroupManagement/<string:userID>/<string:groupName>",
                              ['DELETE', 'POST'], "modifyUserGroup"),
                             (UserGroupManagement, "/api/userGroupManagement/<string:userID>",
                              ['GET'], "getUserGroup"),
                             (PersonalDetail, "/api/personalDetail")
                             ])
