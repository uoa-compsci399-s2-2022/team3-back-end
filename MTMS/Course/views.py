from typing import List

import werkzeug

from MTMS.Models.courses import Course, CourseUser
from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from flask_restful import Resource, reqparse, inputs
from MTMS.Course.services import add_course, modify_course_info, delete_Course, delete_Term, get_Allcourses, \
    get_Allterms, add_CourseUser, modify_CourseUser, get_user_enrolment, \
    get_course_user_by_courseID_isPublish, \
    get_enrolment_role, get_user_enrolment_in_term, delete_CourseUser, get_course_by_id, Term, exist_termName, \
    get_course_user_by_roleInCourse, get_course_by_term, get_user_metaData, get_termName_termID, \
    get_CourseBy_userID, get_course_user_with_public_information, Load_Courses, \
    get_simple_course_by_term, get_simple_course_by_term_and_position, get_simple_course_by_courseNum, \
    get_the_course_working_hour
from MTMS.Term.services import get_available_term, modify_Term, get_user_term, get_term_now, add_term
from MTMS.Utils.utils import dateTimeFormat, get_user_by_id
from MTMS.Auth.services import auth, get_permission_group
from MTMS.Utils.validator import non_empty_string
from MTMS.Models.users import Users
from flask import request

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
    register_api_blueprints(app, "Course", __name__, [
        (CourseManagement, "/api/courseManagement", ["POST", "GET"], "CourseManagement"),
        (CourseManagement, "/api/courseManagement/<int:courseID>", ["PUT"], "ModifyCourseManagement"),
        (deleteCourse, "/api/deleteCourse/<int:courseID>"),
        (EnrolmentManagement, "/api/enrolment"),
        (GetUserEnrolment, "/api/getUserEnrolment/<string:userID>"),
        (GetCurrentUserEnrolment, "/api/getUserEnrolment"),
        (GetCourseUser, "/api/getCourseUser/<int:courseID>/<string:isPublished>"),
        (GetCourseUserWithPublishInformation, "/api/getCourseUserWithPublishInformation/<int:courseID>"),
        (GetCourseByTerm, "/api/getCourseByTerm/<int:termID>"),
        (GetCourse, "/api/getCourse/<int:courseID>"),
        (GetCourseCardMetaData, "/api/GetCourseCardMetaData/<int:courseID>"),
        (GetCourseByUserIDTermID, "/api/GetCourseByUserIDTermID/<string:user_id>/<int:term_id>"),
        (GetCurrentUserEnrollByTerm, "/api/getCurrentUserEnrollByTerm/<int:term_id>"),
        (UploadCourse, "/api/uploadCourse/<int:termID>"),
        (GetSimpleCourseByTerm, "/api/getSimpleCourseByTerm/<int:termID>"),
        (GetSimpleCourseByTermAndPosition, "/api/getSimpleCourseByTermAndPosition/<int:termID>/<string:position>"),
        (GetSimpleCourseByNum, "/api/getSimpleCourseByNum/<int:termID>/<string:courseNum>/<string:position>"),
        (GetCurrentUserWorkingHours, "/api/getCurrentUserWorkingHours/<int:course_id>/<string:role>"),
    ])
