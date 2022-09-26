from MTMS.Models.users import Users, Groups, Permission
from MTMS.Models.courses import RoleInCourse


def set_default_value(db_session):
    # Add Groups
    adminGroup = Groups(groupName='admin')
    student = Groups(groupName='student')
    courseCoordinator = Groups(groupName='courseCoordinator')
    tutorCoordinator = Groups(groupName='tutorCoordinator')
    markerCoordinator = Groups(groupName='markerCoordinator')
    db_session.add_all([
        student,
        courseCoordinator,
        tutorCoordinator,
        markerCoordinator,
        adminGroup])

    # Add test user
    adminUser = Users(id="admin", password="admin")
    adminUser.groups.append(adminGroup)
    db_session.add(adminUser)
    studentUser = Users(id="stu1", password="stu1")
    studentUser.groups.append(student)
    db_session.add(studentUser)

    # Add permission
    UserGroupManagement = Permission(name="UserGroupManagement")
    GetEveryStudentProfile = Permission(name="GetEveryStudentProfile")
    GetAllUser = Permission(name="GetAllUser")
    AddUser = Permission(name="AddUser")
    ChangeEveryUserProfile = Permission(name="ChangeEveryUserProfile")
    NewApplication = Permission(name="NewApplication")
    EditAnyApplication = Permission(name="EditAnyApplication")
    AddCourse = Permission(name="AddCourse")
    EditAnyCourse = Permission(name="EditAnyCourse")
    RoleInCourseManagement = Permission(name="RoleInCourseManagement")
    SendEmail = Permission(name="SendEmail")
    UserGroupManagement.groups = [adminGroup,tutorCoordinator,markerCoordinator]
    GetEveryStudentProfile.groups = [adminGroup,tutorCoordinator,markerCoordinator,courseCoordinator]
    GetAllUser.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    AddUser.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    ChangeEveryUserProfile.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    NewApplication.groups = [student, adminGroup]
    EditAnyApplication.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    AddCourse.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    RoleInCourseManagement.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    EditAnyCourse.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    SendEmail.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator, student]
    db_session.add_all([
        UserGroupManagement,
        GetEveryStudentProfile,
        GetAllUser,
        AddUser,
        ChangeEveryUserProfile,
        NewApplication,
        EditAnyApplication,
        AddCourse,
        RoleInCourseManagement,
        EditAnyCourse,
        SendEmail
    ])

    # Add PersonalDetail
    # AcademicRecord = PersonalDetailSetting(name="Academic record", type=ProfileTypeEnum.File)
    # CV = PersonalDetailSetting(name="CV", type=ProfileTypeEnum.File)
    # UPI = PersonalDetailSetting(name="UPI", type=ProfileTypeEnum.String)
    # AUID = PersonalDetailSetting(name="AUID", type=ProfileTypeEnum.String)
    # CurrentlyOverseas = PersonalDetailSetting(name="Currently Overseas", type=ProfileTypeEnum.Boolean)
    # WillBackToNZ = PersonalDetailSetting(name="Will come arrive back in NZ", type=ProfileTypeEnum.Boolean)
    # CurrentlyOverseas.subProfile = [WillBackToNZ]
    # db_session.add_all([
    #     AcademicRecord,
    #     CV,
    #     UPI,
    #     AUID,
    #     CurrentlyOverseas,
    #     WillBackToNZ
    # ])


    # Add RoleInCourse
    studentRole = RoleInCourse(Name="student")
    tutor = RoleInCourse(Name="tutor")
    marker = RoleInCourse(Name="marker")
    courseCoordinator = RoleInCourse(Name="courseCoordinator")
    db_session.add_all([
        studentRole,
        tutor,
        marker,
        courseCoordinator
    ])


    db_session.commit()
    print("successful Import Default Values!")
