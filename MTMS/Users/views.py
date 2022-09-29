from flask_restful import reqparse, Resource
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints, get_user_by_id
from MTMS.Utils.validator import empty_or_email
from MTMS.Models.users import Users
from MTMS.Auth.services import auth, get_permission_group
# from .services import get_student_profile_now_by_id, change_student_profile


# class StudentPersonalDetail(Resource):
#     @auth.login_required()
#     def get(self, student_id):
#         """
#         get the student personal detail field
#         ---
#         tags:
#           - Users
#         parameters:
#           - name: student_id
#             in: path
#             required: true
#             schema:
#               type: string
#         responses:
#           200:
#             schema:
#         security:
#           - APIKeyHeader: ['Authorization']
#         """
#         if get_user_by_id(student_id) is None:
#             return {"message": "This student could not be found."}, 404
#
#         current_user: Users = auth.current_user()
#         if current_user.id == student_id or len(
#                 set(current_user.groups) & set(get_permission_group("GetEveryStudentProfile"))) > 0:
#             return get_student_profile_now_by_id(student_id), 200
#         else:
#             return "Unauthorized Access", 403
#
#     @auth.login_required()
#     def put(self, student_id):
#         """
#         change the student personal detail
#         ---
#         tags:
#           - Users
#         parameters:
#           - name: student_id
#             in: path
#             required: true
#             schema:
#               type: string
#           - in: body
#             name: body
#             required: true
#             schema:
#               properties:
#                 fields:
#                   type: array
#                   items:
#                     properties:
#                       profileName:
#                         type: string
#                       value:
#                         type: string
#         responses:
#           200:
#             schema:
#               message:
#                   type: string
#         security:
#           - APIKeyHeader: ['Authorization']
#         """
#         if get_user_by_id(student_id) is None:
#             return {"message": "This student could not be found."}, 404
#
#         current_user: Users = auth.current_user()
#         if current_user.id == student_id or len(
#                 set(current_user.groups) & set(get_permission_group("GetEveryStudentProfile"))) > 0:
#             parser = reqparse.RequestParser()
#             args = parser.add_argument('fields', type=list, location='json', required=True,
#                                        help="Did not change any user profile") \
#                 .parse_args()
#             profile_list = args["fields"]
#             if len(profile_list) == 0:
#                 return {"message": "Did not give any student personal detail"}, 400
#             if change_student_profile(student_id, profile_list):
#                 return {"message": "Student Profile has been changed"}, 200
#             else:
#                 return {"message": "Error"}, 400
#         else:
#             return "Unauthorized Access", 403
#



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
                set([g.groupName for g in current_user.groups]) & set(get_permission_group("ChangeEveryUserProfile"))) > 0:
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
                            ])
