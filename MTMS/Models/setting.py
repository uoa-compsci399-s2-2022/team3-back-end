from MTMS.Models import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table, event, Enum
from sqlalchemy.orm import relationship
from MTMS.Utils.enums import EmailCategory, EmailStatus
from MTMS.Utils.utils import dateTimeFormat


class Setting(Base):
    __tablename__ = 'setting'
    settingID = Column(Integer, primary_key=True)
    uniqueEmail = Column(Boolean, default=False)
    allowRegister = Column(Boolean, default=True)

    def serialize(self):
        return {
            'uniqueEmail': self.uniqueEmail,
            'allowRegister': self.allowRegister
        }



class Email_Delivery_Status(Base):
    __tablename__ = 'email_delivery_status'
    emailDeliveryStatusID = Column(Integer, primary_key=True)
    receiver_user_id = Column(Integer, ForeignKey('users.id'))
    sender_user_id = Column(Integer, ForeignKey('users.id'))
    email = Column(String(255))
    category = Column(Enum(EmailCategory))
    status = Column(Enum(EmailStatus))
    error_message = Column(String(65535))
    createdDateTime = Column(DateTime)
    task_id = Column(String(255))

    ReceiverUser = relationship("Users", foreign_keys=[receiver_user_id], back_populates="ReceiverEmailDeliveryStatus")
    SenderUser = relationship("Users", foreign_keys=[sender_user_id], back_populates="SenderEmailDeliveryStatus")

    def serialize(self):
        if self.category is not None:
            category = self.category.value
        else:
            category = None

        if self.status is not None:
            status = self.status.value
        else:
            status = None

        return {
            'emailDeliveryStatusID': self.emailDeliveryStatusID,
            'receiver_user_id': self.receiver_user_id,
            'sender_user_id': self.sender_user_id,
            'email': self.email,
            'category': category,
            'status': status,
            'createdDateTime': dateTimeFormat(self.createdDateTime),
            'error_message': self.error_message,
            'receiver_groups': [g.groupName for g in self.ReceiverUser.groups] if self.ReceiverUser is not None else None,
            'receiver_name': self.ReceiverUser.name if self.ReceiverUser is not None else None,
            'receiver_upi': self.ReceiverUser.upi if self.ReceiverUser is not None else None,
            'receiver_auid': self.ReceiverUser.auid if self.ReceiverUser is not None else None,
            'task_id': self.task_id
        }


@event.listens_for(Setting, 'before_insert')
def reject_before_insert_listener(mapper, connection, target):
    length = connection.execute('select count(*) from setting').scalar()
    if length > 0:
        raise Exception('You can not insert a setting')


@event.listens_for(Setting, 'before_delete')
def reject_before_delete_listener(mapper, connection, target):
    raise Exception('You can not delete a setting')
