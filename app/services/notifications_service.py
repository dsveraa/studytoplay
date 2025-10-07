from sqlalchemy import desc
from app.models import NuevaNotificacion, Notificaciones


class NotificationRepository:
    def __init__(self, db_session):
        self.db = db_session

    def save_notification(self, user_id, message):
        notification = Notificaciones(
            usuario_id=user_id, notificacion=message, leida=False
        )
        self.db.add(notification)

    def activate_alert(self, user_id):
        notification = NuevaNotificacion.query.filter_by(usuario_id=user_id).first()
        if notification:
            notification.estado = True

    def uncheck_new_notification(self, user_id):
        notification_obj = NuevaNotificacion.query.filter_by(usuario_id=user_id).first()
        if notification_obj:
            notification_obj.estado = False
    
    def get_all_notifications(self, user_id):
        return (
            Notificaciones.query
            .filter_by(usuario_id=user_id)
            .order_by(desc(Notificaciones.fecha))
            .all()
        )
    
    @staticmethod
    def get_link_request_notification_object(student_id, request_id):
        return (
            Notificaciones.query
            .filter(
                Notificaciones.usuario_id == student_id,
                Notificaciones.notificacion.like(f'%acciones-{request_id}%')
            )
            .first()
        )

    def commit(self):
        self.db.commit()


class NotifyMessageFactory:
    @staticmethod
    def create_grade_message(action, grade, subject, amount, currency, symbol):
        messages = {
            "add": f"You'll receive <b>{symbol}{amount} {currency}</b> for your <b>{grade}</b> in <b>{subject.capitalize()}</b>!",
            "pay": f"You've been rewarded with <b>{symbol}{amount} {currency}</b> for a grade of <b>{grade}</b> in <b>{subject.capitalize()}</b>!",
        }
        if action not in messages:
            raise ValueError("Invalid action. Expected 'add' or 'pay'.")
        return messages[action]


class Notification:
    def __init__(self, id, repo: NotificationRepository):
        self.id = id
        self.repo = repo

    def notify_grade(self, grade, subject, action, amount, currency, symbol):
        message = NotifyMessageFactory.create_grade_message(action, grade, subject, amount, currency, symbol)
        self.repo.save_notification(self.id, message)
        self.repo.activate_alert(self.id)
        self.repo.commit()

    def uncheck_new_notification(self):
        self.repo.uncheck_new_notification(self.id)
        self.repo.commit()

    @staticmethod
    def delete_link_request_icons(student_id, request_id):
        notification = NotificationRepository.get_link_request_notification_object(student_id, request_id)

        if notification:
            import re
            notification.notificacion = re.sub(
                rf'<span id="acciones-{request_id}".*?</span>',
                '',
                notification.notificacion,
                flags=re.DOTALL
            )