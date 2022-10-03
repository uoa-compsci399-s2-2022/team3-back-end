from MTMS import db_session
from MTMS.Models.users import Users, Groups, InviteUserSaved
from MTMS.Utils.validator import empty_or_email

#
#
#
#
# def invite_user(userList):
#     for i in userList:
#
#
#


def get_group_by_name(name):
    group = db_session.query(Groups).filter(Groups.groupName == name).one_or_none()
    return group


def save_attr_ius(i, ius):
    print(ius.index, i)
    for k in i:
        if k in ['_X_ROW_KEY', 'index']:
            continue
        elif k == 'email':
            try:
                empty_or_email(i[k])
                ius.email = i[k]
                continue
            except ValueError as e:
                db_session.rollback()
                return False, e.args[0], 400
        elif k == 'groups':
            if not i[k]:
                continue
            ius.Groups = []
            for g in i[k]:
                group = get_group_by_name(g)
                if not group:
                    db_session.rollback()
                    return False, "Group not found", 404
                ius.Groups.append(group)
        else:
            if hasattr(ius, k):
                setattr(ius, k, i[k])
            else:
                db_session.rollback()
                return False, f"Update Records Error: The column '{k}' was not found", 404
    return True, None, None


def validate_ius(iusList: list[InviteUserSaved]):
    for i in iusList:
        if not i.email:
            return False, "Email is empty", 400
        try:
            empty_or_email(i.email)
        except ValueError as e:
            return False, e.args[0], 400

        if not i.userID:
            return False, "User ID is empty", 400

        if not i.name:
            return False, "Name is empty", 400

        if not i.Groups:
            return False, "Groups is empty", 400
    return True, None, None
