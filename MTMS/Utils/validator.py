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