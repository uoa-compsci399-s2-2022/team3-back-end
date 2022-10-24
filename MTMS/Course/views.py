from typing import List
import werkzeug
from MTMS.Models.courses import Course, CourseUser
from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from flask_restful import Resource, reqparse, inputs
from MTMS.Course.services import add_course, modify_course_info, delete_Course, get_Allcourses, \
    get_course_by_id, get_course_user_by_roleInCourse, get_course_by_term, get_termName_termID, \
    Load_Courses, \
    get_simple_course_by_term, get_simple_course_by_term_and_position, get_simple_course_by_courseNum, \
    get_available_course_by_term
from MTMS.Utils.utils import dateTimeFormat
from MTMS.Auth.services import auth, get_permission_group
from MTMS.Utils.validator import non_empty_string

course_request = reqparse.RequestParser()
course_request.add_argument('totalAvailableHours', type=float, location='json', required=False) \
    .add_argument('estimatedNumOfStudents', type=int, location='json', required=False, ) \
    .add_argument('currentlyNumOfStudents', type=int, location='json', required=False) \
    .add_argument('needTutors', type=bool, location='json', required=False) \
    .add_argument('needMarkers', type=bool, location='json', required=False) \
    .add_argument('numOfAssignments', type=int, location='json', required=False) \
    .add_argument('numOfLabsPerWeek', type=int, location='json', required=False) \
    .add_argument('numOfTutorialsPerWeek', type=int, location='json', required=False) \
    .add_argument('tutorResponsibility', type=str, location='json', required=False) \
    .add_argument('markerResponsibility', type=str, location='json', required=False) \
    .add_argument('canPreAssign', type=bool, location='json', required=False) \
    .add_argument('markerDeadLine', type=inputs.datetime_from_iso8601, location='json', required=False) \
    .add_argument('tutorDeadLine', type=inputs.datetime_from_iso8601, location='json', required=False) \
    .add_argument('prerequisite', type=str, location='json', required=False)


class CourseManagement(Resource):
    '''
    Course CRUD
    '''

    @auth.login_required(role=get_permission_group("AddCourse"))
    def post(self):
        """
           add a course to the Course table
           ---
           tags:
             - Course
           parameters:
             - in: body
               name: body
               required: true
               schema:
                 id: courseSchema
                 properties:
                     courseNum:
                       type: string
                     courseName:
                       type: string
                     termID:
                       type: integer
                     totalAvailableHours:
                       type: number
                     estimatedNumOfStudents:
                       type: integer
                     currentlyNumOfStudents:
                       type: integer
                     needTutors:
                       type: boolean
                     needMarkers:
                       type: boolean
                     numOfAssignments:
                       type: integer
                     numOfLabsPerWeek:
                       type: integer
                     numOfTutorialsPerWeek:
                       type: integer
                     tutorResponsibility:
                       type: string
                     markerResponsibility:
                       type: string
                     canPreAssign:
                       type: boolean
                     markerDeadLine:
                       type: string
                       format: date-time
                     tutorDeadLine:
                       type: string
                       format: date-time
                     prerequisite:
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
        args = course_request.add_argument('courseNum', type=non_empty_string, location='json', required=True,
                                           help="courseNum cannot be empty") \
            .add_argument("courseName", type=non_empty_string, location='json', required=True) \
            .add_argument("termID", type=int, location='json', required=True, help="termID cannot be empty") \
            .parse_args()
        modify_info = filter_empty_value(args)
        response = add_course(modify_info)
        if response[0]:
            return {"message": response[1]}, 200
        else:
            return {"message": response[1]}, 400

    @auth.login_required
    def put(self, courseID):
        """
        update a course in the Course table
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: courseID
            required: true
            schema:
              type: integer
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/courseSchema'
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        security:
            - APIKeyHeader: ['Authorization']
        """
        args = course_request.add_argument('courseNum', type=str, location='json', required=False, ) \
            .add_argument("courseName", type=str, location='json', required=False) \
            .add_argument("termID", type=int, location='json', required=False) \
            .parse_args()

        current_user = auth.current_user()
        if current_user in get_course_user_by_roleInCourse(courseID, ["courseCoordinator"]) or len(
                set([g.groupName for g in current_user.groups]) & set(get_permission_group("EditAnyCourse"))) > 0:
            modify_info = filter_empty_value(args)
            response = modify_course_info(modify_info, courseID)
            if response[0]:
                return {"message": response[1]}, 200
            else:
                return {"message": response[1]}, 400
        else:
            return {"message": "Unauthorized Access"}, 403

    @auth.login_required()
    def get(self):
        """
        get all courses in the Course table
        ---
        tags:
            - Course
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        security:
            - APIKeyHeader: ['Authorization']
        """
        response = get_Allcourses()
        return response, 200


class GetCourse(Resource):
    @auth.login_required
    def get(self, courseID):
        """
        get a course
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: courseID
            required: true
            schema:
              type: integer
        responses:
            404:
                schema:
                    properties:
                        message:
                            type: string
            200:
                schema:
                  $ref: '#/definitions/courseSchema'
        security:
            - APIKeyHeader: ['Authorization']
        """
        course: Course = get_course_by_id(courseID)
        if course is None:
            return {"message": "course not found"}, 404
        else:
            result = course.serialize()
            courseCoordinators: List[CourseUser] = get_course_user_by_roleInCourse(courseID, ["courseCoordinator"])
            courseCoordinatorsOutput = [c.serialize_with_user_information() for c in courseCoordinators]
            result.update({"courseCoordinators": courseCoordinatorsOutput})
            return result, 200


class GetCourseByTerm(Resource):
    @auth.login_required
    def get(self, termID):
        """
        get courses by term
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: termID
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
        response = get_course_by_term(termID)
        return response, 200


class GetAvailableCourseByTermRole(Resource):
    @auth.login_required
    def get(self, termID, roleName):
        """
        get available courses by term
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: termID
            required: true
            schema:
              type: integer
          - in: path
            name: roleName
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
        """
        response = get_available_course_by_term(termID, roleName)
        if response[0]:
            return response[1], response[2]
        else:
            return {"message": response[1]}, response[2]


class GetSimpleCourseByTerm(Resource):
    @auth.login_required
    def get(self, termID):
        """
        get simple courses by term
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: termID
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
        response = get_simple_course_by_term(termID)
        return response, 200


class GetSimpleCourseByTermAndPosition(Resource):
    @auth.login_required
    def get(self, termID, position):
        """
        get simple courses by term and position
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: termID
            required: true
            schema:
              type: integer
          - in: path
            name: position
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
        """
        position = position.lower()
        if position not in ["marker", "tutor", "all"]:
            return {"message": "position must be marker, tutor or all"}, 400
        response = get_simple_course_by_term_and_position(termID, position)
        return response, 200


class GetSimpleCourseByNum(Resource):
    @auth.login_required()
    def get(self, termID, courseNum, position):
        """
        get simple courses by term
        ---
        tags:
            - Course
        parameters:
          - in: path
            name: termID
            required: true
            schema:
              type: integer
          - in: path
            name: courseNum
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
        """
        position = position.lower()
        if position not in ["marker", "tutor", "all"]:
            return {"message": "position must be marker, tutor or all"}, 400
        response = get_simple_course_by_courseNum(termID, courseNum, position)
        return response, 200


class deleteCourse(Resource):
    @auth.login_required(role=get_permission_group("EditAnyCourse"))
    def delete(self, courseID):
        """
        delete a course from the Course table
        ---
        tags:
            - Course
        parameters:
            - name: courseID
              schema:
                    type: integer
              in: path
              required: true
        responses:
            200:
              schema:
                properties:
                  message:
                    type: string
        security:
            - APIKeyHeader: ['Authorization']
        """
        response = delete_Course(courseID)
        return {"message": response[1]}, response[2]


class UploadCourse(Resource):
    @auth.login_required(role=get_permission_group("AddCourse"))
    def post(self, termID):
        '''
        upload course from csv file
        ---
        tags:
            - Course
        parameters:
            - file: CSV file
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
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        file = args['file']
        filename = werkzeug.utils.secure_filename(file.filename)
        filetype = filename.split('.')[-1]
        if filetype in ["xlsx", "xls", "csv"]:
            # feedback = []
            feedback = Load_Courses(termID, file)
            for i in feedback:
                print(i)
            return {'message': feedback}, 200
        else:
            return {'message': 'file type error. Only accept "xlsx", "xls", "csv" type '}, 400


def register(app):
    '''
    resource[ model, url, methods, endpoint ]
    '''
    register_api_blueprints(app, "Course", __name__, [
        (CourseManagement, "/api/courseManagement", ["POST", "GET"], "CourseManagement"),
        (CourseManagement, "/api/courseManagement/<int:courseID>", ["PUT"], "ModifyCourseManagement"),
        (deleteCourse, "/api/deleteCourse/<int:courseID>"),
        (GetCourseByTerm, "/api/getCourseByTerm/<int:termID>"),
        (GetAvailableCourseByTermRole, "/api/getAvailableCourseByTerm/<int:termID>/<string:roleName>"),
        (GetCourse, "/api/getCourse/<int:courseID>"),
        (UploadCourse, "/api/uploadCourse/<int:termID>"),
        (GetSimpleCourseByTerm, "/api/getSimpleCourseByTerm/<int:termID>"),
        (GetSimpleCourseByTermAndPosition, "/api/getSimpleCourseByTermAndPosition/<int:termID>/<string:position>"),
        (GetSimpleCourseByNum, "/api/getSimpleCourseByNum/<int:termID>/<string:courseNum>/<string:position>")
    ])
