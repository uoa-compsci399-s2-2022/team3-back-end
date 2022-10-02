import json
import re

from email_validator import validate_email, EmailNotValidError
from cerberus import Validator
GRADE = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "CPL", "Pass", "D+", "D", "D-", "DNC", "DNS", "Fail"]


def empty_or_email(email_str):
    if not email_str.strip():
        return email_str
    try:

        validate_email(email_str)
        return email_str
    except EmailNotValidError:
        raise ValueError('{} is not a valid email'.format(email_str))


def email(email_str):
    if not email_str:
        return email_str
    try:

        validate_email(email_str)
        return email_str
    except EmailNotValidError:
        raise ValueError('{} is not a valid email'.format(email_str))

def non_empty_string(s):
    if not s:
        raise ValueError("Must not be empty string")
    return s


def grade(grade_str):
    if grade_str in GRADE:
        return grade_str
    else:
        raise ValueError(f'{grade_str} is not a valid grade')


def application_course_list(list):
    LEARNED_SCHEMA = {
        'courseid' : {'required': True, 'type': 'integer'},
        'haslearned' : {'required': True, 'type': 'boolean'},
        'grade': {'required': True, 'type': 'string'},
        'preexperience': {'required': True, 'type': 'string'},
        'preference': {'required': True, 'type': 'integer'},
    }
    NON_LEARNED_SCHEMA = {
        'courseid': {'required': True, 'type': 'integer'},
        'haslearned': {'required': True, 'type': 'boolean'},
        'explanation': {'required': True, 'type': 'string'},
        'preexperience': {'required': True, 'type': 'string'},
        'preference': {'required': True, 'type': 'integer'},
    }
    for c in list:
        lower_temp_dict = {}
        for k in c:
            lower_temp_dict[k.lower()] = c[k]
        if "haslearned" not in lower_temp_dict.keys():
            raise ValueError('haslearned must be existed')
        elif type(lower_temp_dict["haslearned"]) != bool:
            raise ValueError('haslearned must be boolean')

        if lower_temp_dict["haslearned"]:
            v = Validator(LEARNED_SCHEMA)
            if not v.validate(lower_temp_dict):
                raise ValueError(json.dumps(v.errors))
        else:
            v = Validator(NON_LEARNED_SCHEMA)
            if not v.validate(lower_temp_dict):
                raise ValueError(json.dumps(v.errors))

        if lower_temp_dict["grade"] not in GRADE:
            raise ValueError(f"{lower_temp_dict['grade']} is not a valid grade")
    return list



# check the validation of the email
def is_email(email):
    str = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    if re.match(str, email):
        return True
    else:
        return False

def is_UOA_email_format(email):
    email = email.split('@auckland.ac.nz')
    if len(email) == 2 and email[1] == '':
        return True
    else:
        return False
