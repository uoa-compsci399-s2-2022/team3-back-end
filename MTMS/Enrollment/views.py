from flask_restful import Resource, reqparse

from MTMS.Auth.services import auth
from MTMS.Course.services import add_CourseUser, get_course_by_id, modify_CourseUser, delete_CourseUser, \
    get_user_enrolment, get_course_user_by_courseID_isPublish, get_course_user_with_public_information, \
    get_CourseBy_userID, get_the_course_working_hour
from MTMS.Enrollment.services import modify_estimated_hours
from MTMS.Models.users import Users
from MTMS.Utils.utils import filter_empty_value, get_user_by_id, register_api_blueprints


class EnrolmentManagement(Resource):
    def post(self):
        """
        enrol a student or courseCoordinator to the course
        ---
        tags:
            - Enrolment
        parameters:
          - in: body
            name: body
            required: true
            schema:
              id: enrolmentSchema
              properties:
                courseID:
                  type: integer
                userID:
                  type: string
                role:
                  type: string
        responses:
          200:
            schema:
              properties:
                message:
                  type: string
        """
        parser = reqparse.RequestParser()
        args = parser.add_argument("courseID", type=int, location='json', required=True,
                                   help="courseNum cannot be empty") \
            .add_argument("userID", type=str, location='json', required=True, help="userID cannot be empty") \
            .add_argument("role", type=str, location='json', required=True) \
            .parse_args()
        try:
            response = add_CourseUser(args['courseID'], args['userID'], args['role'])
            return {"message": response[1]}, response[2]
        except:
            return {"message": "Unexpected Error"}, 400

    def put(self):
        """
        modify user role in the course
        ---
        tags:
            - Enrolment
        parameters:
          - in: body
            name: body
            required: true
            schema:
              properties:
                courseID:
                  type: integer
                userID:
                  type: string
                role:
                  type: array
                  items:
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
            args = parser.add_argument("courseID", type=int, location='json', required=True,
                                       help="courseNum cannot be empty") \
                .add_argument("userID", type=str, location='json', required=True, help="userID cannot be empty") \
                .add_argument("role", type=list, location='json', required=True, help='role cannot be empty') \
                .parse_args()
            filter_dict = filter_empty_value(args)
            if len(filter_dict) != 3:
                return {"message": "JSON format error."}, 400

            course = get_course_by_id(args['courseID'])
            if course is None:
                return {"message": "course not found"}, 400
            user = get_user_by_id(args['userID'])
            if user is None:
                return {"message": "user not found"}, 400
            response = modify_CourseUser(course, user, args['role'])
            return {"message": response[1]}, response[2]
        except:
            return {"message": "Unexpected Error"}, 400

    def delete(self):
        """
        delete enrolment
        ---
        tags:
            - Enrolment
        parameters:
            - in: body
              name: body
              required: true
              schema:
                $ref: '#/definitions/enrolmentSchema'
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        """
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument("courseID", type=int, location='json', required=True,
                                       help="courseNum cannot be empty") \
                .add_argument("userID", type=str, location='json', required=True, help="userID cannot be empty") \
                .add_argument("role", type=str, location='json', required=True, help='roleID cannot be empty') \
                .parse_args()
            response = delete_CourseUser(args['courseID'], args['userID'], args['role'])
            return {"message": response[1]}, response[2]
        except:
            return {"message": "Unexpected Error"}, 400


class GetUserEnrolment(Resource):
    def get(self, userID):
        """
        get the user enrolment information
        ---
        tags:
            - Enrolment
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
        """
        if get_user_by_id(userID):
            enrolment_list = get_user_enrolment(userID)
            return enrolment_list, 200
        else:
            return {"message": "This user could not be found."}, 404


class GetCurrentUserEnrolment(Resource):
    @auth.login_required
    def get(self):
        """
        get the current user enrolment information
        ---
        tags:
            - Enrolment
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        security:
              - APIKeyHeader: ['Authorization']
        """
        # try:
        currentUser: Users = auth.current_user()
        if currentUser:
            enrolment_list = get_user_enrolment(currentUser.id)
            return enrolment_list, 200
        # except:
        #     return {"message": "Unexpected Error"}, 400


class GetCourseUser(Resource):
    @auth.login_required
    def get(self, courseID, isPublished):
        """
        get the course's user list
        ---
        tags:
            - Enrolment
        parameters:
            - name: courseID
              in: path
              required: true
              schema:
                    type: integer
            - name: isPublished
              in: path
              required: true
              schema:
                type: boolean
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        """

        try:
            if isPublished.lower() in ['true', 'false']:
                isPublished = isPublished.lower() == 'true'
            else:
                return {"message": "isPublished must be boolean"}, 400
            if get_course_by_id(courseID) is not None:
                return get_course_user_by_courseID_isPublish(courseID, isPublished), 200
            else:
                return {"message": "This courseID could not be found."}, 404
        except:
            return {"message": "Unexpected Error"}, 400


class GetCourseUserWithPublishInformation(Resource):
    @auth.login_required
    def get(self, courseID):
        """
        get the course's user list (with publish information)
        ---
        tags:
            - Enrolment
        parameters:
            - name: courseID
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
        """
        try:
            if get_course_by_id(courseID) is not None:
                res = get_course_user_with_public_information(courseID)
                if res[0]:
                    return res[1], res[2]
                else:
                    return {"message": res[1]}, res[2]
            else:
                return {"message": "This courseID could not be found."}, 404
        except:
            return {"message": "Unexpected Error"}, 400


class GetCourseByUserIDTermID(Resource):
    def get(self, user_id, term_id):
        '''
        get all the course by user id
        ---
        tags:
            - Course
        parameters:
            - name: user_id
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
        '''
        courses = get_CourseBy_userID(user_id, term_id)
        return courses, 200


class GetCurrentUserEnrollByTerm(Resource):
    @auth.login_required()
    def get(self, term_id):
        '''
        get all the course by current user and term id
        ---
        tags:
            - Enrolment
        parameters:
            - name: term_id
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
        '''
        currentUser = auth.current_user()
        courses = get_CourseBy_userID(currentUser.id, term_id)
        return courses, 200


class ModifyEstimatedHours(Resource):
    @auth.login_required()
    def put(self, course_id, user_id, roleName, estimated_hours):
        '''
        modify the estimated hours of an enrollment
        ---
        tags:
            - Course
        parameters:
            - name: course_id
                in: path
                required: true
                schema:
                    type: integer
            - name: user_id
                in: path
                required: true
                schema:
                    type: string
            - name: roleName
                in: path
                required: true
                schema:
                    type: string
            - name: estimated_hours
                in: path
                required: true
                schema:
                    type: number
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        security:
              - APIKeyHeader: ['Authorization']
        '''
        response = modify_estimated_hours(course_id, user_id, roleName, estimated_hours)
        return {"message": response[1]}, response[2]


class GetCurrentUserWorkingHours(Resource):
    @auth.login_required()
    def get(self, course_id, role):
        '''
        get current user working hours (is published)
        ---
        tags:
            - Enrolment
        parameters:
            - name: course_id
              in: path
              required: true
              schema:
                    type: integer
            - name: role
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
        '''
        currentUser = auth.current_user()
        res = get_the_course_working_hour(currentUser, course_id, role, True)
        if res[0]:
            return res[1], 200
        else:
            return {'message': res[1]}, res[2]


def register(app):
    '''
    resource[ model, url, methods, endpoint ]
    '''
    register_api_blueprints(app, "Enrollment", __name__, [
        (EnrolmentManagement, "/api/enrolment"),
        (GetUserEnrolment, "/api/getUserEnrolment/<string:userID>"),
        (GetCurrentUserEnrolment, "/api/getUserEnrolment"),
        (GetCourseUser, "/api/getCourseUser/<int:courseID>/<string:isPublished>"),
        (GetCourseUserWithPublishInformation, "/api/getCourseUserWithPublishInformation/<int:courseID>"),
        (GetCourseByUserIDTermID, "/api/GetCourseByUserIDTermID/<string:user_id>/<int:term_id>"),
        (GetCurrentUserEnrollByTerm, "/api/getCurrentUserEnrollByTerm/<int:term_id>"),
        (GetCurrentUserWorkingHours, "/api/getCurrentUserWorkingHours/<int:course_id>/<string:role>"),
        (ModifyEstimatedHours,
         ["/api/modifyEstimatedHours/<int:course_id>/<string:user_id>/<string:roleName>/<float:estimated_hours>",
          "/api/modifyEstimatedHours/<int:course_id>/<string:user_id>/<string:roleName>/<int:estimated_hours>"])

    ])
