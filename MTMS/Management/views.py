from typing import List

from flask import current_app
from flask_restful import Resource, fields, marshal, reqparse
from MTMS import db_session, cache
from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from MTMS.Models.users import Users, Groups
from MTMS.Auth.services import auth, get_permission_group
from .services import get_user_by_id, get_group_by_name, add_group, delete_group, add_RoleInCourse, \
    get_All_RoleInCourse, \
    delete_RoleInCourse, modify_RoleInCourse, get_user_by_courseID, get_user_by_courseID_roleID, get_all_settings, \
    modify_setting, get_user_sending_status
from MTMS.Utils.validator import non_empty_string
from celery.result import AsyncResult

from ..Models.setting import Email_Delivery_Status
from ..Utils.enums import EmailStatus

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

    @auth.login_required(role=get_permission_group("UserGroupManagement"))
    def put(self, userID):
        """
        modify the user group
        ---
        tags:
          - Management
        parameters:
          - name: userID
            in: path
            required: true
            schema:
              type: string
          - name: body
            in: body
            required: true
            schema:
              properties:
                groups:
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
        user: Users = get_user_by_id(userID)
        if not user:
            return {"message": "This user could not be found."}, 404
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('groups', type=non_empty_string, action='append', required=True)
            args = parser.parse_args()
        except ValueError:
            return {"message": "Invalid input"}, 400
        groups = []
        for g in args['groups']:
            group = get_group_by_name(g)
            if not group:
                db_session.rollback()
                return {"message": "Some of groups could not be found."}, 404
            groups.append(group)
        user.groups = groups
        db_session.commit()
        return {"message": "Successful"}, 200


class RoleInCourse(Resource):
    @auth.login_required(role=get_permission_group("RoleInCourseManagement"))
    def post(self):
        """
        add a role to the RoleInCourse table
        ---
        tags:
            - Management
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                Name:
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
        args = reqparse.RequestParser() \
            .add_argument("Name", type=str, location='json', required=True, help="roleName cannot be empty") \
            .parse_args()

        response = add_RoleInCourse(args['Name'])
        return {"message": response[1]}, response[2]

    @auth.login_required(role=get_permission_group("RoleInCourseManagement"))
    def put(self):
        """
        modify a roleName in the RoleInCourse table
        ---
        tags:
            - Management
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                roleID:
                  type: integer
                Name:
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
        args = reqparse.RequestParser() \
            .add_argument("roleID", type=int, location='json', required=True, help="roleID cannot be empty") \
            .add_argument("Name", type=non_empty_string, location='json', required=True,
                          help="roleName cannot be empty") \
            .parse_args()

        response = modify_RoleInCourse(filter_empty_value(args))
        return {"message": response[1]}, response[2]

    @auth.login_required()
    def get(self):
        """
        get all roles in roleInCourse table
        ---
        tags:
            - Management
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        try:
            roleList = get_All_RoleInCourse()
            return roleList, 200
        except:
            return {"message": "Unexpected Error"}, 400

    @auth.login_required(role=get_permission_group("RoleInCourseManagement"))
    def delete(self, roleID):
        """
        delete a role in the RoleInCourse table
        ---
        tags:
            - Management
        parameters:
            - name: roleID
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
        if 1 <= roleID <= 4:
            return {"message": "Cannot delete core Role"}, 400
        response = delete_RoleInCourse(roleID)
        return {"message": response[1]}, response[2]


class Setting(Resource):
    def get(self):
        """
        get all settings
        ---
        tags:
          - Management
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
                settings:
                  type: array
        security:
          - APIKeyHeader: ['Authorization']
        """
        settings = get_all_settings()
        return settings, 200

    @auth.login_required(role=get_permission_group("Setting"))
    def put(self):
        """
        modify a setting
        ---
        tags:
          - Management
        parameters:
          - name: body
            in: body
            required: true
            schema:
              properties:
                settingID:
                  type: integer
                value:
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
        parser = reqparse.RequestParser()
        parser.add_argument('uniqueEmail', type=bool, required=False, location='json')
        parser.add_argument('allowRegister', type=bool, required=False, location='json')
        parser.add_argument('onlyOneTimeApplication', type=bool, required=False, location='json')
        args = parser.parse_args()
        res = modify_setting(args)
        return {"message": res[1]}, res[2]


class SendingStatus(Resource):
    @auth.login_required(role=get_permission_group("SendingStatus"))
    def get(self):
        """
        get all sending status (current user)
        ---
        tags:
          - Management
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
                sendingStatus:
                  type: array
        security:
          - APIKeyHeader: ['Authorization']
        """
        currentUser = auth.current_user()
        sendingStatus = get_user_sending_status(currentUser)
        return sendingStatus, 200


class DeleteEmailSending(Resource):
    @auth.login_required(role=get_permission_group("SendingStatus"))
    def get(self, category: str):
        """
        stop email sending (current user)
        ---
        tags:
          - Management
        parameters:
          - name: category
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
        currentUser = auth.current_user()
        if category.lower().strip() == 'all':
            emailDStatus: List[Email_Delivery_Status] = db_session.query(Email_Delivery_Status).filter(
                Email_Delivery_Status.sender_user_id == currentUser.id,
                Email_Delivery_Status.status == EmailStatus.sending.value).all()
        else:
            emailDStatus: List[Email_Delivery_Status] = db_session.query(Email_Delivery_Status).filter(
                Email_Delivery_Status.sender_user_id == currentUser.id,
                Email_Delivery_Status.status == EmailStatus.sending.value, Email_Delivery_Status.category == category).all()
        for em in emailDStatus:
            try:
                if current_app.config["CELERY_BROKER_URL"] and current_app.config["CELERY_BROKER_URL"].strip():
                    task_result = AsyncResult(em.task_id)
                    task_result.revoke(terminate=True)
                db_session.delete(em)
                db_session.commit()
            except Exception as e:
                print(e)
                db_session.rollback()
                return 'Failed to delete', 400

        return "Success", 200


# class Send_Email_WholeCourse(Resource):
#     '''
#     admin, course coordinator can send email to all students in a course
#
#     they can choose what role to the course they want to send email to
#
#     eg, course coordinator sent email to all students in the course to hiring marker
#     course coordiantor sent email to all marker to publish a mission.
#     '''
#     def post(self):
#         """
#         post email to all students in a course
#         ---
#         tags:
#             - Email Mangement
#         parameters:
#             - name: courseID
#               in: path
#               required: true
#               schema:
#                     type: integer
#         responses:
#             200:
#                 schema:
#                     properties:
#                         message:
#                             type: string
#         security:
#           - APIKeyHeader: ['Authorization']
#         """
#         args = reqparse.RequestParser()
#         parser = args.add_argument("courseID", type=int, location='json', required=True, help="courseID cannot be empty")\
#         .add_argument("roleID", type=int, location='json', required=True).parse_args()
#
#         courseID = parser['courseID']
#         roleID = parser['roleID']
#         users = get_user_by_courseID_roleID(courseID, roleID)
#
#         status = Send_Email(users, "Test4sending email to the selected students in a selected course")
#         return status[1], status[2]


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Management", __name__,
                            [(UserGroupManagement, "/api/userGroupManagement/<string:userID>/<string:groupName>",
                              ['DELETE', 'POST'], "modifyUserGroup"),
                             (UserGroupManagement, "/api/userGroupManagement/<string:userID>",
                              ['GET', 'PUT'], "getUserGroup"),
                             (RoleInCourse, "/api/roleInCourseManagement", ['POST', 'PUT', 'GET'],
                              "roleInCourseManagement"),
                             (RoleInCourse, "/api/roleInCourseManagement/<int:roleID>", ['DELETE'],
                              "roleInCourseManagementDelete"),
                             (Setting, "/api/setting"),
                             (SendingStatus, "/api/sendingStatus"),
                             (DeleteEmailSending, "/api/deleteEmailSending/<string:category>")
                             # (Send_Email_WholeCourse, "/api/sendEmailWholeCourse"),
                             ])
