from MTMS.utils.utils import register_api_blueprints, filter_empty_value
from flask_restful import Resource, reqparse, inputs

from MTMS.Course.services import add_course, add_term, modify_course_info, delete_Course, delete_Term, get_Allcourses, \
    get_Allterms, modify_Term, add_CourseUser, modify_CourseUser, get_CourseUser, delete_CourseUser, add_RoleInCourse, \
    get_RoleInCourse, delete_RoleInCourse, modify_RoleInCourse
from MTMS.Course.services import Course, Term
from MTMS.utils.utils import valid_semester_format, datetime_format
import datetime

course_request = reqparse.RequestParser()
course_request.add_argument('courseNum', type=str, location='json', required=True,
                            help="courseNum cannot be empty") \
    .add_argument("courseName", type=str, location='json', required=True, help="courseName cannot be empty") \
    .add_argument("termID", type=int, location='json', required=True, help="termID cannot be empty") \
    .add_argument('totalAvailableHours', type=float, location='json', required=False) \
    .add_argument('estimatedNumOfStudent', type=int, location='json', required=False) \
    .add_argument('currentlyNumOfStudent', type=int, location='json', required=False) \
    .add_argument('needTutors', type=bool, location='json', required=False) \
    .add_argument('needMarkers', type=bool, location='json', required=False) \
    .add_argument('numOfAssignments', type=int, location='json', required=False) \
    .add_argument('numOfLabsPerWeek', type=int, location='json', required=False) \
    .add_argument('numOfTutorialsPerWeek', type=int, location='json', required=False) \
    .add_argument('tutorResponsibility', type=str, location='json', required=False) \
    .add_argument('markerResponsibility', type=str, location='json', required=False) \
    .add_argument('canPreAssign', type=bool, location='json', required=False) \
    .add_argument('deadLine', type=inputs.datetime_from_iso8601, location='json', required=False) \



class CourseManagement(Resource):
    '''
    Course 增查改
    '''

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
             properties:
                 courseNum:
                   type: string
                 courseName:
                   type: string
                 termID:
                   type: integer
                 totalAvailableHours:
                   type: number
                 estimatedNumOfStudent:
                   type: string
                 currentlyNumOfStudent:
                   type: integer
                 needTutors:
                   type: string
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
                   type: boolean
       responses:
         200:
           schema:
             properties:
               message:
                 type: string
       """
        try:
            args = course_request.parse_args()
            new_course = Course(courseNum=args['courseNum'], courseName=args['courseName'], termID=args['termID'])
            response = add_course(new_course)
            print(response['mes'])
            if response['status'] == True:
                return {"message": "Successful"}, 200
            else:
                return {"message": "Failed, Course {} existed in term {}".format(new_course.courseNum,
                                                                                 new_course.termID)}, 400
        except:
            return {"message": "failed"}, 400

    def put(self):
        """
        update a course in the Course table
        ---
        tags:
            - Course
        parameters:
            - name: courseNum
              in: path
              required: true
              schema:
                type: string
            - name: courseName
              in: path
              required: true
              schema:
                type: string
            - name: termID
              in: path
              required: true
              schema:
                type: int
        responses:
            200:
                schema:
                    properties:
                        message:
                            type: string

        """
        # modify the courseName
        try:
            args = course_request.parse_args()

            modify_info = {}  # which course's information we need to modifiy
            for key, value in args.items():
                if value != None:
                    modify_info[key] = value

            response = modify_course_info(modify_info)
            if response['status']:
                return {"message": "Successful"}, 200
            else:
                return {"message": "Failed, {} in term {} does not existed".format(
                    modify_info['courseNum'], modify_info['termID']
                )}, 400
        except:
            return {"message": "failed"}, 400

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
        try:
            response = get_Allcourses()
            return response, 200
        except:
            return {"message": "failed"}, 400


class deleteCourse(Resource):
    '''
    Course 删
    '''

    def delete(self, courseNum, termID):
        """
        delete a course from the Course table
        ---
        tags:
            - Course

        parameters:
            - name: courseNum
              schema:
                    type: string
              in: path
              required: true
            - name: termID
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
        try:
            response = delete_Course(courseNum, termID)
            if response['status']:
                print(response['mes'])
                return {"message": "Successful"}, 200
            else:
                print(response['mes'])
                return {"message": "Failed, {} in term {} does not existed".format(
                    courseNum, termID
                )}, 400
        except:
            return {"message": "failed"}, 400


class TermManagement(Resource):
    '''Term 增删查改'''

    def post(self):
        """
        add a term to the Term table
        ---
        tags:
            - Course
        parameters:
            - name: termName
              in: path
              required: true
              schema:
                type: string
            - name: startDate
              in: path
              required: true
              schema:
                    type: string
            - name: endDate
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
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument("termName", type=str, location='json', required=True,
                                       help="termName cannot be empty") \
                .add_argument("termStartDate", type=str, location='json', required=True,
                              help="startDate cannot be empty") \
                .add_argument("termEndDate", type=str, location='json', required=True, help="endDate cannot be empty") \
                .parse_args()

            if not valid_semester_format(args['termName']):
                return {
                           "message": "termName format is not valid. Enter Semester One, Semester Two, Summer Semester"}, 400
            else:
                termStartDate = datetime.strptime(args['termStartDate'], '%Y-%m-%d')
                termEndDate = datetime.strptime(args['termEndDate'], '%Y-%m-%d')
                # termEndDate = datetime_format(args['termEndDate'])
                new_term = Term(termName=args['termName'], termStartDate=termStartDate, termEndDate=termEndDate)
                response = add_term(new_term)
                print(response['mes'])
                return {"message": "Successful"}, 200

        except:
            return {"message": "fail"}, 400

    def delete(self):
        """
        delete a term from the Term table
        ---
        tags:
            - Course
        parameters:
            - name: termName
              in: path
              required: true
              schema:
                type: string
            - name: startDate
              in: path
              required: true
              schema:
                    type: string
            - name: endDate
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
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument("termName", type=str, location='json', required=True,
                                       help="termName cannot be empty") \
                .add_argument("termStartDate", type=str, location='json', required=True,
                              help="startDate cannot be empty") \
                .add_argument("termEndDate", type=str, location='json', required=True, help="endDate cannot be empty") \
                .parse_args()

            if not valid_semester_format(args['termName']):
                return {
                           "message": "termName format is not valid. Enter Semester One, Semester Two, Summer Semester"}, 400
            else:

                termStartDate = datetime_format(args['termStartDate'])
                termEndDate = datetime_format(args['termEndDate'])

                response = delete_Term(args['termName'], termStartDate, termEndDate)
                if response['status']:
                    print(response['mes'])
                    return {"message": "Successful"}, 200
                else:
                    print(response['mes'])
                    return {"message": "Failed, {} does not existed".format(
                        args['termName']
                    )}, 400
        except:
            return {"message": "fail"}, 400

    def get(self):
        """
        get all terms in the Term table
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
        try:
            response = get_Allterms()
            print(response['mes'])
            return {"message": response}, 200
        except:
            return {"message": "failed"}, 400


class modifyTerm(Resource):
    '''改'''

    def put(self, termID):
        '''
        modify a term in the Term table
        ---
        tags:
            - Course
        parameters:
            - name: termID
              in: path
              required: true
              schema:
                    type: integer
            - name: termName
              in: path
              required: true
              schema:
                    type: string
            - name: startDate
              in: path
              required: true
              schema:
                    type: string
            - name: endDate
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

        '''
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument("termName", type=str, location='json', required=False,
                                       help="termName cannot be empty") \
                .add_argument("termStartDate", type=str, location='json', required=False,
                              help="startDate cannot be empty") \
                .add_argument("termEndDate", type=str, location='json', required=False, help="endDate cannot be empty") \
                .parse_args()
            modify_info = {}
            for key, value in args.items():
                if value:
                    try:
                        value = datetime_format(value)  # convert string to datetime.date
                        modify_info[key] = value
                    except:
                        modify_info[key] = value
            print(modify_info)
            response = modify_Term(termID, modify_info)
            return {"message": response['mes']}, 200
        except:
            return {"message": "failed"}, 400


class CourseUserManagement(Resource):
    def post(self):
        """
        add a courseUser to the CourseUser table
        ---
        tags:
            - CourseUser
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


        """
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument("courseID", type=int, location='json', required=True,
                                       help="courseNum cannot be empty") \
                .add_argument("userID", type=str, location='json', required=True, help="userID cannot be empty") \
                .add_argument("roleID", type=int, location='json', required=False) \
                .parse_args()

            if args['roleID'] == None:
                response = add_CourseUser(args['courseID'], args['userID'])
            else:
                response = add_CourseUser(args['courseID'], args['userID'], args['roleID'])
            print(response['mes'])
            return {"message": 'successful'}, 200
        except:
            return {"message": "failed"}, 400

    def put(self):
        """
        modify a courseUser in the CourseUser table
        ---
        tags:
            - CourseUser
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

        """
        try:
            parser = reqparse.RequestParser()
            args = parser.add_argument("courseID", type=int, location='json', required=True,
                                       help="courseNum cannot be empty") \
                .add_argument("userID", type=str, location='json', required=True, help="userID cannot be empty") \
                .add_argument("roleID", type=int, location='json', required=True, help='roleID cannot be empty') \
                .parse_args()

            filter_dict = filter_empty_value(args)

            response = modify_CourseUser(filter_dict)
            if response['status']:
                print(response['mes'])
                return {"message": 'successful'}, 200
            else:
                print(response['mes'])
                return {"message": 'failed'}, 400
        except:
            return {"message": "failed"}, 400

    def get(self):
        """
        get  courseUsers in the CourseUser table
        ---
        tags:
            - CourseUser
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
            response = get_CourseUser(args['courseID'], args['userID'])
            if response['status']:
                print(response['mes'])
                return {"message": response['mes']}, 200
            else:
                print(response['mes'])
                return {"message": 'failed'}, 400
        except:
            return {"message": "failed"}, 400

    def delete(self):
        """
        delete a courseUser in the CourseUser table
        ---
        tags:
            - CourseUser
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
            return {"message": "failed"}, 400


class RoleInCourse(Resource):
    def post(self):
        """
        add a role to the RoleInCourse table
        ---
        tags:
            - RoleInCourse
        parameters:
            - name: Name
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
        args = reqparse.RequestParser() \
            .add_argument("Name", type=str, location='json', required=True, help="roleName cannot be empty") \
            .parse_args()

        response = add_RoleInCourse(args['Name'])
        if response['status']:
            print(response['mes'])
            return {"message": 'successful'}, 200
        else:
            print(response['mes'])
            return {"message": 'failed'}, 400

    def put(self):
        """
        modify a role in the RoleInCourse table
        ---
        tags:
            - RoleInCourse
        parameters:
            - name: roleID
              in: path
              required: true
              schema:
                    type: integer
            - name: Name
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
        args = reqparse.RequestParser() \
            .add_argument("roleID", type=int, location='json', required=True, help="roleID cannot be empty") \
            .add_argument("Name", type=str, location='json', required=True, help="roleName cannot be empty") \
            .parse_args()

        respone = modify_RoleInCourse(filter_empty_value(args))
        if respone['status']:
            print(respone['mes'])
            return {"message": 'successful'}, 200
        else:
            print(respone['mes'])
            return {"message": 'failed'}, 400

    def get(self):
        """
        get a role in the RoleInCourse table
        ---
        tags:
            - RoleInCourse
        parameters:
            - name: roleID
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
        args = reqparse.RequestParser() \
            .add_argument("roleID", type=int, location='json', required=True, help="roleID cannot be empty") \
            .parse_args()
        response = get_RoleInCourse(args['roleID'])
        if response['status']:
            print(response['mes'])
            return {"message": response['mes']}, 200
        else:
            print(response['mes'])
            return {"message": 'failed'}, 400

    def delete(self):
        """
        delete a role in the RoleInCourse table
        ---
        tags:
            - RoleInCourse
        parameters:
            - name: roleID
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
        args = reqparse.RequestParser() \
            .add_argument("roleID", type=int, location='json', required=True, help="roleID cannot be empty") \
            .parse_args()
        response = delete_RoleInCourse(args['roleID'])
        if response['status']:
            print(response['mes'])
            return {"message": 'successful'}, 200
        else:
            print(response['mes'])
            return {"message": 'failed'}, 400


def register(app):
    '''
    resource[ model, url, methods, endpoint ]
    '''
    register_api_blueprints(app, "Course", __name__, [
        (CourseManagement, "/api/CourseManagement", ["POST", "PUT", "GET"], "CourseManagement"),
        (deleteCourse, "/api/deleteCourse/<string:courseNum>/<int:termID>", ['DELETE'], 'deleteCourse'),

        (TermManagement, "/api/TermManagement", ['POST', 'DELETE', 'GET'], 'TermManagement'),
        (modifyTerm, "/api/modifyTerm/<int:termID>", ['PUT'], 'modifyTerm'),

        (CourseUserManagement, "/api/CourseUserManagement", ['POST', 'PUT', 'GET', 'DELETE'], 'CourseUserManagement'),

        (RoleInCourse, "/api/RoleInCourse", ['POST', 'PUT', 'GET', 'DELETE'], 'RoleInCourse'),
    ])
