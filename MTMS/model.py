import datetime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class User(Base):
    __tablename__ = 'User'
    id = Column(String, primary_key=True)
    password = Column(String)
    email = Column(String)
    name = Column(String)
    createDateTime = Column(DateTime)

    def __init__(self, id=None, password=None, email=None, name=None, createDateTime=None):
        self.id = id
        self.password = generate_password_hash(password)
        self.email = email
        self.name = name
        self.createDateTime = createDateTime

