from typing import List

import config
from MTMS import celery, db_session
from MTMS.Application.services import get_application_by_id, send_application_result_email
from MTMS.Models.courses import CourseUser
from MTMS.Models.setting import Email_Delivery_Status
from MTMS.Models.users import InviteUserSaved, Users
from MTMS.Users.services import send_invitation_email
from MTMS.Utils.enums import EmailCategory, EmailStatus
from MTMS.Utils.utils import generate_random_password, create_email_sending_status



if config.Config.CELERY_BROKER_URL:
    @celery.task(bind=True)
    def send_email_celery(self, ius, currentUser):
        from MTMS import db_session
        ius_email_status = []
        for ius_id in ius:
            i: InviteUserSaved = db_session.query(InviteUserSaved).filter(InviteUserSaved.id == ius_id).first()
            email_status: Email_Delivery_Status = create_email_sending_status(i.userID, EmailCategory.invite_user,
                                                                              i.email, currentUser, self.request.id)
            if email_status is None or not email_status[0]:
                return {"message": "Create email sending status error"}, 500
            ius_email_status.append((i, email_status[1]))
        for (i, email_status) in ius_email_status:
            password = generate_random_password()
            try:
                send_invitation_email(i.email, i.name, i.userID, password)
                user = Users(
                    email=i.email,
                    name=i.name,
                    id=i.userID,
                    password=password,
                )
                user.groups = i.Groups
                db_session.add(user)
                db_session.delete(i)
                db_session.commit()
                email_status.status = EmailStatus.sent
                db_session.commit()
            except Exception as e:
                print(e)
                db_session.rollback()
                try:
                    email_status.status = EmailStatus.failed
                    email_status.error_message = str(e)
                    db_session.commit()
                except Exception as e:
                    db_session.rollback()
                continue
        return {"message": "Success"}, 200


    @celery.task(bind=True)
    def send_application_result_email_celery(self, args, currentUser):
        for a in args:
            application = get_application_by_id(a)
            email_status: Email_Delivery_Status = create_email_sending_status(application.Users.id,
                                                                              EmailCategory.application_result,
                                                                              application.Users.email, currentUser,
                                                                              self.request.id)
            if email_status is None or not email_status[0]:
                return {"message": "Create email sending status error"}, 500
            try:
                courseUsers: List[CourseUser] = application.course_users

                send_application_result_email(application.Users.email, application.Users.id, application.Users.name,
                                              application.Term.termName, application.type, application.status)

                for cu in courseUsers:
                    cu.isPublished = True
                application.isResultPublished = True
                db_session.commit()
                email_status[1].status = EmailStatus.sent
                db_session.commit()
            except Exception as e:
                print(e)
                db_session.rollback()
                try:
                    email_status[1].status = EmailStatus.failed
                    email_status[1].error_message = str(e)
                    db_session.commit()
                except Exception as e:
                    print(e)
                    db_session.rollback()
                continue
        return "Success", 200
