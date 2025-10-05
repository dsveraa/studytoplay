from flask import render_template, session, Blueprint

from app.services.notifications_service import Notification, NotificationRepository
from app.utils.helpers import login_required

from .. import db


notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notifications')
@login_required
def notifications():
    user_id = session.get('usuario_id')
    repo = NotificationRepository(db.session)
    notification = Notification(user_id, repo)
    notification.uncheck_new_notification()
    query = repo.get_all_notifications(user_id)
    return render_template("notificaciones.html", notificaciones=query)
