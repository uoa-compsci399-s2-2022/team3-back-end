from MTMS.Models.users import Users, Groups, Permission
from MTMS.Models.courses import RoleInCourse
from MTMS.Models.setting import Setting


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
    DeleteUser = Permission(name="DeleteUser")
    ApplicationApproval = Permission(name="ApplicationApproval")
    InviteStudent = Permission(name="InviteStudent")
    InviteCC = Permission(name="InviteCC")
    InviteTC = Permission(name="InviteTC")
    InviteMC = Permission(name="InviteMC")
    SettingPerm = Permission(name="Setting")

    UserGroupManagement.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    GetEveryStudentProfile.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    GetAllUser.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    AddUser.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    ChangeEveryUserProfile.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    NewApplication.groups = [student, adminGroup]
    EditAnyApplication.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    AddCourse.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    RoleInCourseManagement.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    EditAnyCourse.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    SendEmail.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator, student]
    DeleteUser.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    ApplicationApproval.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    InviteStudent.groups = [adminGroup, tutorCoordinator, markerCoordinator, courseCoordinator]
    InviteCC.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    InviteTC.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    InviteMC.groups = [adminGroup, tutorCoordinator, markerCoordinator]
    SettingPerm.groups = [adminGroup, tutorCoordinator, markerCoordinator]
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
        SendEmail,
        DeleteUser,
        ApplicationApproval,
        InviteStudent,
        InviteCC,
        InviteTC,
        InviteMC,
        SettingPerm
    ])

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

    # Add Setting
    db_session.add(Setting())

    db_session.commit()
    print("successful Import Default Values!")
