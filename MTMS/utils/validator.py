import re

from email_validator import validate_email, EmailNotValidError



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

