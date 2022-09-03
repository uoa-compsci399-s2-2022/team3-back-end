from MTMS.model import Users, Groups, Permission, PersonalDetailSetting
from MTMS.utils import ProfileTypeEnum


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

    # Add admin user
    adminUser = Users(id="admin", password="admin")
    adminUser.groups.append(adminGroup)
    db_session.add(adminUser)

    # Add permission
    UserGroupManagement = Permission(name="UserGroupManagement")

    UserGroupManagement.groups = [adminGroup,tutorCoordinator,markerCoordinator]
    db_session.add_all([
        UserGroupManagement,
    ])

    # Add PersonalDetail
    AcademicRecord = PersonalDetailSetting(name="Academic record", type=ProfileTypeEnum.File)
    CV = PersonalDetailSetting(name="CV", type=ProfileTypeEnum.File)
    Name = PersonalDetailSetting(name="Name", type=ProfileTypeEnum.String)
    UPI = PersonalDetailSetting(name="UPI", type=ProfileTypeEnum.String)
    AUID = PersonalDetailSetting(name="AUID", type=ProfileTypeEnum.String)
    UniversityEmail = PersonalDetailSetting(name="University Email", type=ProfileTypeEnum.Email)
    CurrentlyOverseas = PersonalDetailSetting(name="Currently Overseas", type=ProfileTypeEnum.Boolean)
    WillBackToNZ = PersonalDetailSetting(name="Will come arrive back in NZ", type=ProfileTypeEnum.Boolean)
    CurrentlyOverseas.subProfile = [WillBackToNZ]
    db_session.add_all([
        AcademicRecord,
        CV,
        Name,
        UPI,
        AUID,
        UniversityEmail,
        CurrentlyOverseas,
        WillBackToNZ
    ])



    db_session.commit()
    print("successful Import Default Values!")
