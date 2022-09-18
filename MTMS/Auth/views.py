import datetime
from flask import request, jsonify
from flask_restful import reqparse, Resource
from MTMS import db_session
from MTMS.Utils.utils import register_api_blueprints
from MTMS.Utils.validator import non_empty_string, is_email
from MTMS.Models.users import Users
from . import services
from .services import add_overdue_token, auth, get_permission_group, Exist_userID, register_user, send_validation_email, \
    Exist_user_Email, delete_validation_code


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
        args = parser.add_argument('userID', type=non_empty_string, location='json', required=True, help="userID cannot be empty", trim=True) \
            .add_argument("password", type=non_empty_string, location='json', required=True, help="password cannot be empty", trim=True) \
            .add_argument("email", type=str, location='json', required=False) \
            .add_argument("name", type=str, location='json', required=False) \
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
        user.groups = []
        db_session.add(user)
        db_session.commit()
        return {"message": "User loaded successfully"}, 200

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


class RegisterUser(Resource):
    def post(self):
        """
        Register a new user
        ---
        tags:
            - Auth
        parameters:
            - name : userID
              in : body
              type : string
              required : true
              schema:
                   type: string
            - name : password
              in : body
              type : string
              required : true
              schema:
                   type: string
            - name : email
              in : body
              type : string
              required : true
              schema:
                   type: string
            - name : name
              in : body
              type : string
              required : true
            - code : code
              in : body
              type : string
              required : true
              schema:
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
            args = parser.add_argument('userID', type=non_empty_string, location='json', required=True, help="userID cannot be empty", trim=True) \
                .add_argument("password", type=non_empty_string, location='json', required=True, help="password cannot be empty", trim=True) \
                .add_argument("repeatPassword", type=non_empty_string, location='json', required=True, help="repeatPassword cannot be empty", trim=True) \
                .add_argument("email", type=str, location='json', required=True) \
                .add_argument("name", type=str, location='json', required=True) \
                .add_argument("code", type=str, location='json', required=True) \
                .parse_args()
            if Exist_userID(args['userID']):
                return {"message": "This userID already exists"}, 400
            if args['password'] != args['repeatPassword']:
                return {"message": "The two passwords are inconsistent"}, 400
            if args['name'] == "":
                return {"message": "The name cannot be empty"}, 400
            createDateTime = datetime.datetime.now()
            code = args['code']
            user = Users(id=args['userID'], password=args['password'], email=args['email'], createDateTime=createDateTime, name=args['name'])
            response = register_user(user, code)
            if response["status"] == True:
                return {"message": response["mes"]}, 200
            else:
                return {"message": response["mes"]}, 400
        except:
            return {"message": "Register failed"}, 400

        # email = args['email']
        # if args['password'] != args['repeatPassword']:
        #     return {"message": "The two passwords are inconsistent"}, 400
        # elif is_email(email) ==  False:
        #     return {"message": "The email format is incorrect"}, 400
        # # elif is_UOA_email_format(email) == False:
        # #     return {"message": "The email is not a UOA format"}, 400
        # else:
        #     print(validation_by_email(email))
        #     return {"message": "The email has been sent successfully"}, 200


class Send_validation_email(Resource):
     def post(self):
        """
        send validation email
        ---
        tags:
            - Auth
        parameters:
            - name : email
              in: body
              required: true
              schema:
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
            args = parser.add_argument('email', type=str, location='json', required=True, help="email cannot be empty", trim=True) \
            .parse_args()
            email = args['email']

            if is_email(email) ==  False:
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
                    return {"message":"fail, check your email address"}, 400
        except:
            return {"message": "The email has been sent failed, Check your format"}, 400


class Delete_validation_code(Resource):
    def delete(self):
        '''
        delete the validation code
        ---
        tags:
            - Auth
        parameters:
            - name : email
              in : query
              required : true
              schema:
                type: string
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        '''
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument('email', type=str, location='json', required=True, help="email cannot be empty", trim=True) \
            .parse_args()
            email = args['email']
            if Exist_user_Email(email):
                if is_email(email) ==  False:
                    return {"message": "The email format is incorrect"}, 400
                # elif is_UOA_email_format(email) == False:
                #     return {"message": "The email is not a UOA format"}, 400
                else:
                    response = delete_validation_code(email)
                    if response['status']:
                        return {"message": "The email has been deleted successfully"}, 200
                    else:
                        return {"message":"fail, check your email address"}, 400
            else:
                return {"message": "This email does not exist"}, 400
        except:
            return {"message": "The email has been deleted failed"}, 400

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
                                (User, "/api/users"),
                                (RegisterUser, "/api/registerUser"),
                                (CurrentUser, "/api/currentUser"),
                                (Send_validation_email, "/api/sendValidationEmail"),
                                (Delete_validation_code, "/api/deleteValidationCode")
                            ])
