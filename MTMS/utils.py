from flask import Blueprint
from flask_restful import Api


def register_api_blueprints(app, blueprint_name, blueprint_importName, resource:list):
    test_api_bp = Blueprint(blueprint_name, blueprint_importName)
    api = Api(test_api_bp)
    for r in resource:
        if len(r) == 4:
            api.add_resource(r[0], r[1], methods=r[2], endpoint=r[3])
        elif len(r) == 2:
            api.add_resource(r[0], r[1])
        else:
            raise IndexError
    app.register_blueprint(test_api_bp)
