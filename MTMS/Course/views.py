from MTMS.Utils.utils import register_api_blueprints, filter_empty_value
from flask_restful import Resource, reqparse, inputs

from MTMS.Course.services import add_course, add_term, modify_course_info, delete_Course, delete_Term, get_Allcourses, \
    get_Allterms, modify_Term, add_CourseUser, modify_CourseUser, get_user_enrolment, get_course_user, \
    get_enrolment_role, get_user_enrolment_in_term, delete_CourseUser, get_course_by_id, Term, exist_termName, \
    get_course_user_by_roleInCourse, get_course_by_term, get_available_term, get_user_metaData, get_termName_termID
from MTMS.Utils.utils import dateTimeFormat, get_user_by_id
from MTMS.Auth.services import auth, get_permission_group
from MTMS.Utils.validator import non_empty_string
from MTMS.Models.users import Users

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
    .add_argument('deadLine', type=inputs.datetime_from_iso8601, location='json', required=False) \
    .add_argument('prerequisite', type=str, location='json', required=False) \


class CourseManagement(Resource):
    '''
    Course 增查改
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
                     deadLine:
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
        args = course_request.add_argument('courseNum', type=non_empty_string, location='json', required=False) \
            .add_argument("courseName", type=non_empty_string, location='json', required=False) \
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
            200:
                schema:
                    properties:
                        message:
                            type: string
        """
        course = get_course_by_id(courseID)
        if course is None:
            return {"message": "course not found"}, 404
        else:
            return course.serialize(), 200


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


class AvailableTerm(Resource):
    def get(self):
        """
        get available terms
        ---
        tags:
            - Course
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
                          defaultDeadLine:
                             type: string
                             format: date-time

        """
        try:
            response = get_available_term()
            return response, 200
        except:
            return {"message": "failed"}, 400


class TermManagement(Resource):
    @auth.login_required(role=get_permission_group("AddTerm"))
    def post(self):
        """
        add a term to the Term table
        ---
        tags:
            - Course
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
                   defaultDeadLine:
                     type: string
                     format: date-time
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
            .add_argument("defaultDeadLine", type=inputs.datetime_from_iso8601, location='json', required=False) \
            .parse_args()
        if exist_termName(args['termName']):
            return {"message": f"term {args['termName']} existed"}, 400
        new_term = Term(termName=args['termName'], startDate=args['startDate'], endDate=args['endDate'], isAvailable=args['isAvailable'], defaultDeadLine=args['defaultDeadLine'])
        response = add_term(new_term)
        return {"message": response[1]}, response[2]

    @auth.login_required(role=get_permission_group("AddTerm"))
    def delete(self, termID):
        """
        delete a term from the Term table
        ---
        tags:
            - Course
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
            - Course
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
            - Course
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
            .add_argument("defaultDeadLine", type=inputs.datetime_from_iso8601, location='json', required=False) \
            .parse_args()
        # try:
        modify_info = filter_empty_value(args)
        response = modify_Term(termID, modify_info)
        return {"message": response[1]}, response[2]
        # except:
        #     return {"message": "Unexpected error"}, 400


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

            filter_dict = filter_empty_value(args)

            response = modify_CourseUser(filter_dict)
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
            - name: courseID
              in: path
              required: true
              schema:
                    type: integer
            - name: userID
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
            parser = reqparse.RequestParser()
            args = parser.add_argument("courseID", type=int, location='json', required=True,
                                       help="courseNum cannot be empty") \
                .add_argument("userID", type=str, location='json', required=True, help="userID cannot be empty") \
                .parse_args()
            response = delete_CourseUser(args['courseID'], args['userID'])
            if response['status']:
                print(response['mes'])
                return {"message": 'successful'}, 200
            else:
                print(response['mes'])
                return {"message": 'failed'}, 400
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

        try:
            currentUser: Users = auth.current_user()
            if currentUser:
                enrolment_list = get_user_enrolment(currentUser.id)
                return enrolment_list, 200
        except:
            return {"message": "Unexpected Error"}, 400


class GetCourseUser(Resource):
    @auth.login_required
    def get(self, courseID):
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
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string
        """

        try:
            if get_course_by_id(courseID) is not None:
                return get_course_user(courseID), 200
            else:
                return {"message": "This courseID could not be found."}, 404
        except:
            return {"message": "Unexpected Error"}, 400


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


        MetaData['deadLine'] = dateTimeFormat(course.deadLine)


        MetaData['courseCoordinator'] = coordiantors
        MetaData['marker'] = markers
        MetaData['tutor'] = tutors
        MetaData['student'] = students
        # print(MetaData)
        return MetaData, 200



def register(app):
    '''
    resource[ model, url, methods, endpoint ]
    '''
    register_api_blueprints(app, "Course", __name__, [
        (CourseManagement, "/api/courseManagement", ["POST", "GET"], "CourseManagement"),
        (CourseManagement, "/api/courseManagement/<int:courseID>", ["PUT"], "ModifyCourseManagement"),
        (deleteCourse, "/api/deleteCourse/<int:courseID>"),
        (TermManagement, "/api/term", ['POST', 'GET'], 'TermManagement'),
        (AvailableTerm, "/api/availableTerm"),
        (TermManagement, "/api/term/<int:termID>", ['DELETE'], 'DeleteTermManagement'),
        (modifyTerm, "/api/modifyTerm/<int:termID>"),
        (EnrolmentManagement, "/api/enrolment"),
        (GetUserEnrolment, "/api/getUserEnrolment/<string:userID>"),
        (GetCurrentUserEnrolment, "/api/getUserEnrolment"),
        (GetCourseUser, "/api/getCourseUser/<int:courseID>"),
        (GetCourseByTerm, "/api/getCourseByTerm/<int:termID>"),
        (GetCourse, "/api/getCourse/<int:courseID>"),

        (GetCourseCardMetaData, "/api/GetCourseCardMetaData/<int:courseID>"),
    ])


