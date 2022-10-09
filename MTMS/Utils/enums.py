from enum import Enum


class StudentDegreeEnum(Enum):
    Undergraduate = 1
    Postgraduate = 2


class ApplicationStatus(Enum):
    Unsubmit = 1
    Pending = 2
    Success = 3
    Rejected = 4


class ApplicationType(Enum):
    Marker = 'Marker'
    Tutor = 'Tutor'
