from flask_restful import Resource
from flask_apispec import MethodResource
from flask import Blueprint
from flask_restful import Api

class Resource(MethodResource, Resource):
    """
    This class must be inherited if you want to use flask_restful to build your API and automatically generate Swagger documentation
    """
    pass


def register_api_blueprints(app, blueprint_name, blueprint_importName, swagger_docs, resource:dict):
    test_api_bp = Blueprint(blueprint_name, blueprint_importName)
    api = Api(test_api_bp)
    for k in resource:
        api.add_resource(k, resource[k], endpoint=k.__name__)
    app.register_blueprint(test_api_bp)
    for k in resource:
        swagger_docs.register(k, endpoint=f'{blueprint_name}.{k.__name__}')
