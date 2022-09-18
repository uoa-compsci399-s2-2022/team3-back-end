from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from MTMS.Models import Base


class Application(Base):
    __tablename__ = 'Application'
    ApplicationID = Column(Integer, primary_key=True)
    createdDateTime = Column(DateTime)
    submittedDateTime = Column(DateTime)
    isCompleted = Column(Boolean, nullable=False)
    studentID = Column(ForeignKey("Users.id"))
    Users = relationship("Users", back_populates="Application")

    def serialize(self):
        return {
                "application_id": self.ApplicationID,
                "createdDateTime": self.createdDateTime.isoformat(),
                "submittedDateTime": self.submittedDateTime.isoformat(),
                "isCompleted": self.isCompleted
            }


