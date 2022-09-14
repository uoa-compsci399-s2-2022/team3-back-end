from MTMS import db_session
from MTMS.Models.users import Users, Groups
from MTMS.Models.courses import RoleInCourse
from MTMS.Utils.utils import response_for_services

def get_user_by_id(id):
    user = db_session.query(Users).filter(Users.id == id).one_or_none()
    return user


def get_group_by_name(name):
    group = db_session.query(Groups).filter(Groups.groupName == name).one_or_none()
    return group


def add_group(user, group):
    user.groups.append(group)
    db_session.commit()

def delete_group(user, group):
    user.groups.remove(group)
    db_session.commit()


# RoleInCourse
def add_RoleInCourse(Name):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == Name).first()
    if role == None:
        role = RoleInCourse()
        role.Name = Name
        db_session.add(role)
        db_session.commit()
        return (True, "add '{}' successfully".format(Name), 200)
    else:
        return (False, "'{}' already existed".format(Name), 400)


def get_All_RoleInCourse():
    role = db_session.query(RoleInCourse).all()
    result = []
    for r in role:
        result.append(r.serialize())
    return result




def get_RoleInCourse_by_name(roleName):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.Name == roleName).one_or_none()
    return role


def get_RoleInCourse_by_id(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID).one_or_none()
    return role


def delete_RoleInCourse(roleID):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == roleID)
    if role.first() == None:
        return (False, "'{}' does not existed".format(roleID), 404)
    else:
        role.delete()
        db_session.commit()
        return (True, "delete '{}' successfully".format(roleID), 200)


def modify_RoleInCourse(args: dict):
    role = db_session.query(RoleInCourse).filter(RoleInCourse.roleID == args['roleID'])
    if role.first() == None:
        return (False, "'{}' does not existed".format(args['roleID']), 404)
    else:
        for key, value in args.items():
            role.update(
                {key: value}
            )
        db_session.commit()
        return (True, "INFO:  update '{}' successfully".format(args['roleID']), 200)
