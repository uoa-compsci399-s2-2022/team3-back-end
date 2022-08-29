import datetime
from flask import request
from flask_restful import reqparse, marshal_with
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from MTMS import db_session
from MTMS.utils import Resource, register_api_blueprints
from MTMS.model import User
from . import services, schema
from .services import add_overdue_token, auth





@doc(description='Login Api with Token', tags=['Auth'])
class Login(Resource):
    @use_kwargs({'userID': fields.Str(), 'password': fields.Str()}, location='json')
    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        args = parser.add_argument('userID', type=str, location='json', required=True, help="userID cannot be empty") \
            .add_argument("password", type=str, location='json', required=True, help="password cannot be empty") \
            .parse_args()
        user = services.authenticate(args['userID'], args['password'])
        if user:
            return {"message": "Login Successful", "token": services.generate_token(user)}, 200
        else:
            return {"message": "The userID or password is incorrect"}, 401


@doc(description='Logout Api with Token <br><br>Be sure to call this method when you destroy the token on the front end. '
                 'His purpose is to mark tokens on the server that have been logged out to prevent tokens from being '
                 'attacked before they expire.', tags=['Auth'])
class Logout(Resource):
    @auth.login_required()
    def get(self):
        auth_type, token = request.headers['Authorization'].split(None, 1)
        add_overdue_token(token)
        return {"message": "Logout Successful"}


@doc(description='CRUD User', tags=['Auth'])
class Users(Resource):
    @use_kwargs(schema.userInput(), location='json')
    def post(self, **kwargs):
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
        user = User(
            id=args['userID'],
            password=args['password'],
            email=args['email'],
            createDateTime=datetime.datetime.now(),
            name=args['name']
        )
        db_session.add(user)
        db_session.commit()
        return {"message": "User loaded successfully"}, 200

    @auth.login_required()
    def get(self):
        return {"message": "successfully"}


def register(app, swagger_docs):
    register_api_blueprints(app, "Auth", __name__, swagger_docs,
                            {
                                Login: "/api/login",
                                Logout: "/api/logout",
                                Users: "/api/users"
                            })
