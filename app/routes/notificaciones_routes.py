from flask import render_template, session, Blueprint
from sqlalchemy import desc

from app.models import NuevaNotificacion, Notificaciones
from app.utils.helpers import login_required

from .. import db


notificaciones_bp = Blueprint('notificaciones', __name__)

@notificaciones_bp.route('/notifications')
@login_required
def notifications():
    usuario_id = session.get('usuario_id')
    NuevaNotificacion.query.filter_by(usuario_id=usuario_id).update({ 'estado': False })
    db.session.commit()
    
    query = (
        Notificaciones.query
        .filter_by(usuario_id=usuario_id)
        .order_by(desc(Notificaciones.fecha))
        .all()
    )

    return render_template("notificaciones.html", notificaciones=query)
