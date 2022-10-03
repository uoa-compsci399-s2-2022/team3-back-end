import datetime
from flask import request, jsonify
from flask_restful import reqparse, Resource
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints
from MTMS.Utils.validator import non_empty_string, email
from MTMS.Models.users import Users, Groups
from . import services
from .services import add_overdue_token, auth, get_permission_group, Exist_userID, register_user, send_validation_email, \
    Exist_user_Email, delete_validation_code, get_user_by_id, get_all_groups
from email_validator import validate_email, EmailNotValidError


class Login(Resource):
    """
        Test only:
        userID: admin
        password: admin
        After login by userID and password, the token will be returned.
    """

    def post(self, **kwargs):
        """
        Login Api with Token
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                userID:
                  type: string
                password:
                  type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
                token:
                  type: string
          401:
            schema:
              properties:
                message:
                  type: string
        """
        parser = reqparse.RequestParser()
        args = parser.add_argument('userID', type=str, location='json', required=True, help="userID cannot be empty") \
            .add_argument("password", type=str, location='json', required=True, help="password cannot be empty") \
            .parse_args()
        user = services.authenticate(args['userID'], args['password'])
        if user:
            return {"message": "Login Successful", "token": services.generate_token(user)}, 200
        else:
            return {"message": "The userID or password is incorrect"}, 401


class Logout(Resource):
    @auth.login_required()
    def get(self):
        """
        Logout Api with Token
        Be sure to call this method when you destroy the token on the front end.
        His purpose is to mark tokens on the server that have been logged out to prevent tokens from being
        attacked before they expire.
         ---
        tags:
          - Auth
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        auth_type, token = request.headers['Authorization'].split(None, 1)
        add_overdue_token(token)
        return {"message": "Logout Successful"}


class LoginStatus(Resource):
    def get(self):
        """
        Get the current user's login status
        Three states:
          1. Login
          2. NoLogin
          3. NoToken
        ---
        tags:
          - Auth
        responses:
          200:
            schema:
              type: string
        security:
          - APIKeyHeader: ['Authorization']
        """
        auth_local = auth.get_auth()
        if not auth_local or "token" not in auth_local:
            return "NoToken", 200
        else:
            token = auth_local["token"]
            if services.verify_token(token):
                return "Login", 200
            else:
                return "NoLogin", 200


class CurrentUser(Resource):
    @auth.login_required()
    def get(self):
        """
        get current user
        ---
        tags:
          - Auth
        responses:
          200:
            schema:
              id: userSchema
              type: object
              properties:
                id:
                  type: string
                email:
                  type: string
                name:
                  type: string
                groups:
                  type: array
                  items:
                    type: string
                createDateTime:
                  type: string
                  format: date-time
        security:
          - APIKeyHeader: ['Authorization']
        """
        currentUser = auth.current_user()
        return jsonify(currentUser.serialize())


class User(Resource):
    """
        description:
        - post method: create a new user
        - get method: test the user
    """

    @auth.login_required(role=get_permission_group("AddUser"))
    def post(self):
        """
        create a new user
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                userID:
                  type: string
                password:
                  type: string
                email:
                  type: string
                name:
                  type: string
                groups:
                  type: array
                  items:
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
        args = parser.add_argument('userID', type=non_empty_string, location='json', required=True,
                                   help="userID cannot be empty", trim=True) \
            .add_argument("password", type=non_empty_string, location='json', required=True,
                          help="password cannot be empty", trim=True) \
            .add_argument("email", type=email, location='json', required=True) \
            .add_argument("name", type=str, location='json', required=False) \
            .add_argument("groups", type=list, location='json', required=True) \
            .parse_args()
        user = services.get_user_by_id(args['userID'])
        if user is not None:
            return {"message": "This userID already exists"}, 400
        # Create and store the new User, with password encrypted.
        user = Users(
            id=args['userID'],
            password=args['password'],
            email=args['email'],
            createDateTime=datetime.datetime.now(),
            name=args['name']
        )
        for g in args['groups']:
            group = db_session.query(Groups).filter(Groups.groupName == g).one_or_none()
            if group:
                user.groups.append(group)
            else:
                return {"message": "The group does not exist"}, 400
        db_session.add(user)
        db_session.commit()
        return {"message": "User added successfully"}, 200

    @auth.login_required(role=get_permission_group("GetAllUser"))
    def get(self):
        """
        get all users
        ---
        tags:
          - Auth
        responses:
          200:
            schema:
              type: array
              items:
                $ref: '#/definitions/userSchema'
        security:
          - APIKeyHeader: ['Authorization']
        """
        users = services.get_all_users()
        return jsonify([u.serialize() for u in users])

    @auth.login_required(role=get_permission_group("DeleteUser"))
    def delete(self, userID):
        """
        delete a user
        ---
        tags:
          - Auth
        parameters:
          - in: path
            name: courseID
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
        user = get_user_by_id(userID)
        if user is None:
            return {"message": "This userID does not exist"}, 404
        db_session.delete(user)
        db_session.commit()
        return {"message": "User deleted successfully"}, 200


class RegisterUser(Resource):
    def post(self):
        """
        Register a new user
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                userID:
                  type: string
                password:
                  type: string
                repeatPassword:
                  type: string
                email:
                  type: string
                name:
                  type: string
                code:
                  type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        """

        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument('userID', type=non_empty_string, location='json', required=True,
                                       help="userID cannot be empty", trim=True) \
                .add_argument("password", type=non_empty_string, location='json', required=True,
                              help="password cannot be empty", trim=True) \
                .add_argument("repeatPassword", type=non_empty_string, location='json', required=True,
                              help="repeatPassword cannot be empty", trim=True) \
                .add_argument("email", type=str, location='json', required=True) \
                .add_argument("name", type=str, location='json', required=True) \
                .add_argument("code", type=str, location='json', required=True) \
                .parse_args()
            if get_user_by_id(args['userID']) is not None:
                # 需要和前端说， 90s 后删除验证码
                return {"message": "This userID already exists"}, 400
            if args['password'] != args['repeatPassword']:
                return {"message": "The two passwords are inconsistent"}, 400
            if args['name'] == "":
                return {"message": "The name cannot be empty"}, 400
            createDateTime = datetime.datetime.now()
            code = args['code']
            user = Users(id=args['userID'], password=args['password'], email=args['email'],
                         createDateTime=createDateTime, name=args['name'])
            response = register_user(user, code)
            if response["status"] == True:
                return {"message": response["mes"]}, 200
            else:
                return {"message": response["mes"]}, 400
        except:
            return {"message": "Register failed"}, 400


class Send_validation_email(Resource):
    def post(self):
        """
        Send_validation_email
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                email:
                  type: string

        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        """
        # try:
        parser = reqparse.RequestParser()
        args = parser.add_argument('email', type=str, location='json', required=True, help="email cannot be empty",
                                   trim=True) \
            .parse_args()
        email = args['email']
        if Exist_user_Email(email):
            return {"message": "The email already exists"}, 400

        is_email = True
        try:
            validate_email(email)
        except EmailNotValidError:
            is_email = False

        if not is_email:
            return {"message": "The email format is incorrect"}, 400
        # elif is_UOA_email_format(email) == False:
        #     return {"message": "The email is not a UOA format"}, 400
        else:
            # thr = threading.Thread(target=send_validation_email(email))
            # thr.setDaemon(True) # 守护线程，防止卡死
            # thr.start()
            response = send_validation_email(email)
            if response['status']:
                return {"message": "The email has been sent successfully"}, 200
            else:
                return {"message": "fail, check your email address"}, 400
        # except:
        #     return {"message": "Unexpected Error"}, 400


class Delete_validation_code(Resource):
    def delete(self):
        """
        delete validation code
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                email:
                  type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        """
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument('email', type=str, location='json', required=True, help="email cannot be empty",
                                       trim=True) \
                .parse_args()
            email = args['email']
            if Exist_user_Email(email):
                if is_email(email) == False:
                    return {"message": "The email format is incorrect"}, 400
                # elif is_UOA_email_format(email) == False:
                #     return {"message": "The email is not a UOA format"}, 400
                else:
                    response = delete_validation_code(email)
                    if response['status']:
                        return {"message": "The email has been deleted successfully"}, 200
                    else:
                        return {"message": "fail, check your email address"}, 400
            else:
                return {"message": "This email does not exist"}, 400
        except:
            return {"message": "The email has been deleted failed"}, 400



class Groups_api(Resource):
    def get(self):
        """
        get all groups
        ---
        tags:
          - Auth
        responses:
          200:
            schema:
              type: array
        security:
          - APIKeyHeader: ['Authorization']
        """
        groups = services.get_all_groups()
        return [g.serialize() for g in groups]


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Auth", __name__,
                            [
                                (Login, "/api/login"),
                                (Logout, "/api/logout"),
                                (LoginStatus, "/api/loginStatus"),
                                (User, "/api/users", ["GET", "POST"], "user"),
                                (User, "/api/users/<string:userID>", ["DELETE"], "deleteUser"),
                                (RegisterUser, "/api/registerUser"),
                                (CurrentUser, "/api/currentUser"),
                                (Send_validation_email, "/api/sendValidationEmail"),
                                (Delete_validation_code, "/api/deleteValidationCode"),
                                (Groups_api, "/api/groups")
                            ])
