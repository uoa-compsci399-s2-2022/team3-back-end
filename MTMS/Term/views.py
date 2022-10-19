from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from flask_restful import Resource, reqparse, inputs
from MTMS.Course.services import delete_Term, get_Allterms, exist_termName
from MTMS.Term.services import get_available_term, modify_Term, get_user_term, get_term_now, add_term
from MTMS.Auth.services import auth, get_permission_group
from MTMS.Utils.validator import non_empty_string
from MTMS.Models.courses import Payday, Term


class GetTermNow(Resource):
    def get(self):
        """
        get current term
        ---
        tags:
            - Term
        responses:
            400:
                schema:
                    properties:
                        message:
                            type: string
            200:
                schema:
                  $ref: '#/definitions/termSchema'
        """
        response = get_term_now()
        return response, 200


class TermManagement(Resource):
    @auth.login_required(role=get_permission_group("AddTerm"))
    def post(self):
        """
        add a term to the Term table
        ---
        tags:
            - Term
        parameters:
            - in: body
              name: body
              required: true
              schema:
                 id: termSchemaNoID
                 properties:
                   termName:
                     type: string
                   startDate:
                     type: string
                     format: date
                   endDate:
                     type: string
                     format: date
                   isAvailable:
                     type: boolean
                   defaultMarkerDeadLine:
                     type: string
                     format: date-time
                   defaultTutorDeadLine:
                     type: string
                     format: date-time
                   payday:
                     type: array
                        items:
                           type: date-time
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
        args = parser.add_argument("termName", type=non_empty_string, location='json', required=True,
                                   help="termName cannot be empty") \
            .add_argument("startDate", type=inputs.date, location='json', required=True) \
            .add_argument("endDate", type=inputs.date, location='json', required=True) \
            .add_argument("isAvailable", type=bool, location='json', required=False) \
            .add_argument("defaultMarkerDeadLine", type=inputs.datetime_from_iso8601, location='json', required=False) \
            .add_argument("defaultTutorDeadLine", type=inputs.datetime_from_iso8601, location='json', required=False) \
            .add_argument("payday", type=list, location='json', required=False) \
            .parse_args()
        if exist_termName(args['termName']):
            return {"message": f"term {args['termName']} existed"}, 400
        paydayList = []
        if 'payday' in args and args['payday'] is not None:
            for p in args['payday']:
                try:
                    p = inputs.datetime_from_iso8601(p)
                    paydayList.append(Payday(payday=p))
                except ValueError:
                    return {"message": f"payday {p} is not a valid date"}, 400
        new_term = Term(termName=args['termName'], startDate=args['startDate'], endDate=args['endDate'],
                        isAvailable=args['isAvailable'], defaultMarkerDeadLine=args['defaultMarkerDeadLine'],
                        defaultTutorDeadLine=args['defaultTutorDeadLine'])
        new_term.payday = paydayList
        response = add_term(new_term)
        return {"message": response[1]}, response[2]

    @auth.login_required(role=get_permission_group("AddTerm"))
    def delete(self, termID):
        """
        delete a term from the Term table
        ---
        tags:
            - Term
        parameters:
            - name: termID
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
        try:
            response = delete_Term(termID)
            return {"message": response[1]}, response[2]
        except:
            return {"message": "Exception error"}, 400

    @auth.login_required()
    def get(self):
        """
        get all terms in the Term table
        ---
        tags:
            - Term
        responses:
            200:
                schema:
                   $ref: '#/definitions/termSchema'
        security:
            - APIKeyHeader: ['Authorization']
        """
        # try:
        response = get_Allterms()
        return response, 200
        # except:
        #     return {"message": "failed"}, 400


class modifyTerm(Resource):
    @auth.login_required(role=get_permission_group("AddTerm"))
    def put(self, termID):
        '''
        modify a term in the Term table
        ---
        tags:
            - Term
        parameters:
          - name: termID
            schema:
              type: integer
            in: path
            required: true
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/termSchemaNoID'
        responses:
            200:
                schema:
                    properties:
                    properties:
                        message:
                            type: string
        security:
            - APIKeyHeader: ['Authorization']
        '''

        parser = reqparse.RequestParser()
        args = parser.add_argument("termName", type=str, location='json', required=False,
                                   help="termName cannot be empty") \
            .add_argument("startDate", type=inputs.date, location='json', required=False) \
            .add_argument("endDate", type=inputs.date, location='json', required=False) \
            .add_argument("isAvailable", type=bool, location='json', required=False) \
            .add_argument("defaultMarkerDeadLine", type=inputs.datetime_from_iso8601, location='json', required=False) \
            .add_argument("defaultTutorDeadLine", type=inputs.datetime_from_iso8601, location='json', required=False) \
            .parse_args()
        # try:
        modify_info = filter_empty_value(args)
        response = modify_Term(termID, modify_info)
        return {"message": response[1]}, response[2]
        # except:
        #     return {"message": "Unexpected error"}, 400


class AvailableTerm(Resource):
    def get(self):
        """
        get available terms
        ---
        tags:
            - Term
        responses:
            400:
                schema:
                    properties:
                        message:
                            type: string
            200:
                schema:
                    id: termSchema
                    type: array
                    items:
                      properties:
                          termID:
                             type: integer
                          termName:
                             type: string
                          startDate:
                             type: string
                             format: date
                          endDate:
                             type: string
                             format: date
                          isAvailable:
                             type: boolean
                          defaultMarkerDeadLine:
                             type: string
                             format: date-time
                          defaultTutorDeadLine:
                             type: string
                             format: date-time
        """
        try:
            response = get_available_term()
            return response, 200
        except:
            return {"message": "failed"}, 400


class GetCurrentUserTerm(Resource):
    @auth.login_required()
    def get(self):
        """
        get current user terms
        ---
        tags:
            - Term
        responses:
            400:
                schema:
                    properties:
                        message:
                            type: string
            200:
                schema:
                  $ref: '#/definitions/termSchema'
        """
        currentUser = auth.current_user()
        response = get_user_term(currentUser.id)
        return response, 200


def register(app):
    '''
    resource[ model, url, methods, endpoint ]
    '''
    register_api_blueprints(app, "Term", __name__, [
        (TermManagement, "/api/term", ['POST', 'GET'], 'TermManagement'),
        (TermManagement, "/api/term/<int:termID>", ['DELETE'], 'DeleteTermManagement'),
        (modifyTerm, "/api/modifyTerm/<int:termID>"),
        (GetTermNow, "/api/getTermNow"),
        (GetCurrentUserTerm, "/api/getCurrentUserTerm"),
        (AvailableTerm, "/api/availableTerm"),
    ])
