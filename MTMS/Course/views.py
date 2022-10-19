from typing import List
import werkzeug
from MTMS.Models.courses import Course, CourseUser
from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from flask_restful import Resource, reqparse, inputs
from MTMS.Course.services import add_course, modify_course_info, delete_Course, get_Allcourses, \
    get_course_by_id, get_course_user_by_roleInCourse, get_course_by_term, get_user_metaData, get_termName_termID, \
    Load_Courses, \
    get_simple_course_by_term, get_simple_course_by_term_and_position, get_simple_course_by_courseNum
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
        """
        response = get_Allcourses()
        return response, 200


class GetCourse(Resource):
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
        """
        response = get_course_by_term(termID)
        return response, 200


class GetSimpleCourseByTerm(Resource):
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
        """
        response = get_simple_course_by_term(termID)
        return response, 200


class GetSimpleCourseByTermAndPosition(Resource):
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
        """
        position = position.lower()
        if position not in ["marker", "tutor", "all"]:
            return {"message": "position must be marker, tutor or all"}, 400
        response = get_simple_course_by_term_and_position(termID, position)
        return response, 200


class GetSimpleCourseByNum(Resource):
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
        """
        position = position.lower()
        if position not in ["marker", "tutor", "all"]:
            return {"message": "position must be marker, tutor or all"}, 400
        response = get_simple_course_by_courseNum(termID, courseNum, position)
        return response, 200


class deleteCourse(Resource):
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
        """
        response = delete_Course(courseID)
        return {"message": response[1]}, response[2]


#
# class GetNoPublishedCourseUser(Resource):
#     @auth.login_required
#     def get(self, courseID):
#         """
#         get the course's user list(No Published)
#         ---
#         tags:
#             - Enrolment
#         parameters:
#             - name: courseID
#               in: path
#               required: true
#               schema:
#                     type: integer
#         responses:
#             200:
#                 schema:
#                     properties:
#                         message:
#                             type: string
#         """
#
#         try:
#             if get_course_by_id(courseID) is not None:
#                 return get_course_user(courseID, False), 200
#             else:
#                 return {"message": "This courseID could not be found."}, 404
#         except:
#             return {"message": "Unexpected Error"}, 400


class GetCourseCardMetaData(Resource):
    def get(self, courseID):
        '''
        get all the meta data then show in courseCard to front-end
        should aggregate with users (course coordinators) and courses
        in student view
        ---
        tags:
            - Course
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
        '''
        course = get_course_by_id(courseID)

        # 获取当前课程所有的 courseCoordinator,  marker , tutor and student
        Course_coordiantors = get_course_user_by_roleInCourse(course.courseID, ['courseCoordinator'])
        Course_markers = get_course_user_by_roleInCourse(course.courseID, ['marker'])
        Course_tutors = get_course_user_by_roleInCourse(course.courseID, ['tutor'])
        Course_students = get_course_user_by_roleInCourse(course.courseID, ['student'])

        coordiantors = []
        markers = []
        tutors = []
        students = []

        semester = get_termName_termID(course.termID)

        for coordiantor in Course_coordiantors:
            userData = get_user_metaData(coordiantor.user.id)
            coordiantors.append(userData)

        for marker in Course_markers:
            userData = get_user_metaData(marker.user.id)
            markers.append(userData)

        for tutor in Course_tutors:
            userData = get_user_metaData(tutor.user.id)
            tutors.append(userData)

        for student in Course_students:
            # print(Course_students)
            userData = get_user_metaData(student.user.id)
            students.append(userData)

        MetaData = {}
        MetaData['courseID'] = courseID
        MetaData['courseNum'] = course.courseNum
        MetaData['courseName'] = course.courseName
        MetaData['semester'] = semester

        MetaData['totalAvailableHours'] = course.totalAvailableHours
        MetaData['estimatedNumOfStudents'] = course.estimatedNumOfStudents
        MetaData['currentlyNumOfStudents'] = course.currentlyNumOfStudents
        MetaData['needTutors'] = course.needTutors
        MetaData['needMarkers'] = course.needMarkers
        MetaData['numOfAssignments'] = course.numOfAssignments
        MetaData['numOfLabsPerWeek'] = course.numOfLabsPerWeek
        MetaData['numOfTutorialsPerWeek'] = course.numOfTutorialsPerWeek
        MetaData['tutorResponsibility'] = course.tutorResponsibility
        MetaData['markerResponsibility'] = course.markerResponsibility
        MetaData['canPreAssign'] = course.canPreAssign
        MetaData['prerequisite'] = course.prerequisite

        MetaData['tutorDeadLine'] = dateTimeFormat(course.tutorDeadLine)
        MetaData['markerDeadLine'] = dateTimeFormat(course.markerDeadLine)

        MetaData['courseCoordinator'] = coordiantors
        MetaData['marker'] = markers
        MetaData['tutor'] = tutors
        MetaData['student'] = students
        return MetaData, 200


class UploadCourse(Resource):
    @auth.login_required
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
        (GetCourse, "/api/getCourse/<int:courseID>"),
        (GetCourseCardMetaData, "/api/GetCourseCardMetaData/<int:courseID>"),
        (UploadCourse, "/api/uploadCourse/<int:termID>"),
        (GetSimpleCourseByTerm, "/api/getSimpleCourseByTerm/<int:termID>"),
        (GetSimpleCourseByTermAndPosition, "/api/getSimpleCourseByTermAndPosition/<int:termID>/<string:position>"),
        (GetSimpleCourseByNum, "/api/getSimpleCourseByNum/<int:termID>/<string:courseNum>/<string:position>")
    ])
