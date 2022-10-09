from MTMS.Models import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Table, event
from sqlalchemy.orm import relationship


class Setting(Base):
    __tablename__ = 'setting'
    settingID = Column(Integer, primary_key=True)
    uniqueEmail = Column(Boolean, default=False)
    allowRegister = Column(Boolean, default=True)


@event.listens_for(Setting, 'before_insert')
def reject_before_insert_listener(mapper, connection, target):
    length = connection.execute('select count(*) from setting').scalar()
    if length > 0:
        raise Exception('You can not insert a setting')



@event.listens_for(Setting, 'before_delete')
def reject_before_delete_listener(mapper, connection, target):
    raise Exception('You can not delete a setting')