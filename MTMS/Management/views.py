from flask_restful import Resource, fields, marshal, reqparse
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from MTMS.Models.users import Users, Groups
from MTMS.Auth.services import auth, get_permission_group
from .services import get_user_by_id, get_group_by_name, add_group, delete_group, add_RoleInCourse, \
    get_All_RoleInCourse, \
    delete_RoleInCourse, modify_RoleInCourse, get_user_by_courseID, get_user_by_courseID_roleID
from MTMS.Utils.validator import non_empty_string


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




# class PersonalDetailManagement(Resource):
#     @auth.login_required()
#     def get(self):
#         """
#         get the student personal detail field
#         ---
#         tags:
#           - Management
#         responses:
#           200:
#             schema:
#         security:
#           - APIKeyHeader: ['Authorization']
#         """
#         allPersonalDetail = db_session.query(PersonalDetailSetting).filter(
#             PersonalDetailSetting.superProfileID == None).all()
#         response = [marshal(p.serialize(), PersonalDetail_fields) for p in allPersonalDetail]
#         return response, 200


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
                              ['GET'], "getUserGroup"),
                             # (PersonalDetailManagement, "/api/personalDetailManagement"),
                             (RoleInCourse, "/api/roleInCourseManagement", ['POST', 'PUT', 'GET'], "roleInCourseManagement"),
                                (RoleInCourse, "/api/roleInCourseManagement/<int:roleID>", ['DELETE'], "roleInCourseManagementDelete"),
                                # (Send_Email_WholeCourse, "/api/sendEmailWholeCourse"),
                             ])
