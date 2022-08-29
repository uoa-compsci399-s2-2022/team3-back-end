from flask import Blueprint, render_template, url_for, request, redirect, session, g, current_app
from flask_restful import Api
from flask_apispec import doc, marshal_with
from marshmallow import Schema, fields
from MTMS.utils import Resource, register_api_blueprints


class Sample(Resource):
    @doc(description='My First GET API.', tags=['Sample'])
    def get(self):
        return {'sample': 'Hello world'}






def register(app, swagger_docs):
    register_api_blueprints(app, "Sample", __name__, swagger_docs,
                            {
                                Sample: "/api/"
                            })

