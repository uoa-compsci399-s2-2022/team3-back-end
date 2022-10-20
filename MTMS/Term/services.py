import datetime

from MTMS import db_session
from MTMS.Course.services import get_term_by_id
from MTMS.Models.courses import Term, Course, CourseUser, Payday


def get_available_term():
    terms = db_session.query(Term).filter(Term.isAvailable == True).all()
    terms_list = []
    for i in range(len(terms)):
        terms_list.append(terms[i].serialize())
    return terms_list


def modify_Term(termID, modify_info, paydayList):
    term: Term = get_term_by_id(termID)
    if not term:
        return False, "{} does not existed".format(termID), 404
    else:
        # try:
            term_query = db_session.query(Term).filter(
                Term.termID == termID
            )
            for key, value in modify_info.items():
                term_query.update(
                    {key: value}
                )
            if paydayList:
                for old_payday in term.Paydays:
                    if old_payday not in paydayList:
                        db_session.delete(old_payday)
                for new_payday in paydayList:
                    if new_payday not in term.Paydays:
                        term.Paydays.append(new_payday)
            db_session.commit()
            return True, "update {} successfully".format(termID), 200
        # except Exception as e:
        #     db_session.rollback()
        #     return False, "Update Term Error", 400

def get_user_term(userID):
    userTerm = db_session.query(Term).join(Course).join(CourseUser).filter(CourseUser.userID == userID,
                                                                           CourseUser.isPublished).all()

    return [i.serialize() for i in userTerm]


def get_term_now():
    term = db_session.query(Term).filter(Term.startDate < datetime.datetime.now(tz=datetime.timezone.utc),
                                         Term.endDate > datetime.datetime.now(tz=datetime.timezone.utc)).all()
    return [i.serialize() for i in term]


def add_term(term: Term):
    try:
        db_session.add(term)
        db_session.commit()
        return True, "append {} successfully".format(term.termName), 200
    except Exception as e:
        db_session.rollback()
        return False, "Add Term Error", 500


def get_term_payday(termID):
    term = get_term_by_id(termID)
    if not term:
        return False, "{} does not existed".format(termID), 404
    else:
        payday: Payday = term.Paydays
        payday_list = []
        for i in range(len(payday)):
            payday_list.append(payday[i].serialize())
        return True, payday_list, 200
