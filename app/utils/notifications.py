from app.models import NuevaNotificacion, Notificaciones


class NotificationRepository:
    def __init__(self, db_session):
        self.db = db_session

    def save_notification(self, usuario_id, mensaje):
        notificacion = Notificaciones(
            usuario_id=usuario_id, notificacion=mensaje, leida=False
        )
        self.db.add(notificacion)

    def activate_alert(self, usuario_id):
        nueva = NuevaNotificacion.query.filter_by(usuario_id=usuario_id).first()
        if nueva:
            nueva.estado = True

    def commit(self):
        self.db.commit()


class NotifyGradeMessageFactory:
    @staticmethod
    def create(action, grade, subject):
        messages = {
            "add": f"You're about to receive a prize for your <b>{grade}</b> in <b>{subject.capitalize()}</b>!",
            "pay": f"You have been rewarded for a grade of <b>{grade}</b> in <b>{subject.capitalize()}</b>!",
        }
        if action not in messages:
            raise ValueError("Invalid action. Expected 'add' or 'pay'.")
        return messages[action]


class Notification:
    def __init__(self, id, repo: NotificationRepository):
        self.id = id
        self.repo = repo

    def notify_grade(self, grade, subject, action):
        message = NotifyGradeMessageFactory.create(action, grade, subject)
        self.repo.save_notification(self.id, message)
        self.repo.activate_alert(self.id)
        self.repo.commit()
