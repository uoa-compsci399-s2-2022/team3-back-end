from MTMS import db_session
from MTMS.Models.users import Users, Groups


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