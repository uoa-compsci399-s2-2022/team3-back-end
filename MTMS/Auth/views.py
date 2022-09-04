import datetime
from flask import request, jsonify
from flask_restful import reqparse, marshal_with, Resource, fields, marshal
from MTMS import db_session
from MTMS.utils import register_api_blueprints
from MTMS.model import Users, Groups
from . import services, schema
from .services import add_overdue_token, auth, get_permission_group


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


class CurrentUser(Resource):
    @auth.login_required
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
        args = parser.add_argument('userID', type=str, location='json', required=True, help="userID cannot be empty") \
            .add_argument("password", type=str, location='json', required=True, help="password cannot be empty") \
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


def register(app):
    '''
        restful router.
        eg 127.0.0.1:5000/api/auth/users
    '''
    register_api_blueprints(app, "Auth", __name__,
                            [
                                (Login, "/api/login"),
                                (Logout, "/api/logout"),
                                (User, "/api/users"),
                                (CurrentUser, "/api/currentUser")
                            ])
