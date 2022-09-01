from MTMS.model import Users, Groups, Permission


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

    # Add permission
    UserGroupManagement = Permission(name="UserGroupManagement")
    UserGroupManagement.groups = [adminGroup,tutorCoordinator,markerCoordinator]
    db_session.add_all([
        UserGroupManagement,
    ])


    db_session.add(adminUser)
    db_session.commit()
    print("successful Import Default Values!")
