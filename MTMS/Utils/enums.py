from enum import Enum


class StudentDegreeEnum(Enum):
    Undergraduate = 1
    Postgraduate = 2


class ApplicationStatus(Enum):
    Unsubmit = 1
    Pending = 2
    Accepted = 3
    Rejected = 4


class ApplicationType(Enum):
    marker = 'marker'
    tutor = 'tutor'


class EmailStatus(Enum):
    sending = "sending"
    sent = "sent"
    failed = "failed"


class EmailCategory(Enum):
    invite_user = "invite_user"
    application_result = "application_result"


class ApplicationTime(Enum):
    no_limit = 0
    only_one = 1
    global_setting = 2
