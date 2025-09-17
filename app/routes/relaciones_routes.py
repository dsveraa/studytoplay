from flask import flash, redirect, render_template, request, session, jsonify, Blueprint, url_for
from sqlalchemy import desc
from sqlalchemy.orm import aliased

from app.models import Usuario, SolicitudVinculacion, SupervisorEstudiante, Notificaciones
from app.repositories.user_repository import UserRepository
from app.services.link_request_service import LinkRequestService
from app.services.user_service import UserService
from app.utils.helpers import login_required, supervisor_required, send_link_request_notification, enviar_notificacion_respuesta_lr

from .. import db


relaciones_bp = Blueprint('relaciones', __name__)

@relaciones_bp.route('/received_requests', methods=['GET'])
@login_required
def received_requests():
    usuario_id = session.get('usuario_id')
    
    Supervisor = aliased(Usuario)
    Estudiante = aliased(Usuario)

    solicitud = (
        db.session.query(
            Supervisor.id.label('supervisor_id'),
            Supervisor.nombre.label('supervisor'),
            SolicitudVinculacion.estudiante_id,
            Estudiante.nombre.label('estudiante'),
            SolicitudVinculacion.estado,
            SolicitudVinculacion.fecha_solicitud
        )
        .select_from(Supervisor)
        .join(SolicitudVinculacion, Supervisor.id == SolicitudVinculacion.supervisor_id)
        .join(Estudiante, Estudiante.id == SolicitudVinculacion.estudiante_id)
        .filter(SolicitudVinculacion.estudiante_id == usuario_id)
        .order_by(desc(SolicitudVinculacion.fecha_solicitud))
        .all()
    )
    
    resultado = [
        {
            'supervisor_id': sid,
            'supervisor': supervisor,
            'estudiante_id': eid,
            'estudiante': estudiante,
            'estado': estado,
            'fecha_solicitud': fecha
        }
        for sid, supervisor, eid, estudiante, estado, fecha in solicitud
    ]

    if not solicitud:
        return jsonify({'status': 'error', 'error': 'query not found'}), 400

    return jsonify({'status': 'ok', 'current_requests': resultado})

@relaciones_bp.route('/request_response', methods=['POST'])
@login_required
def request_response():
    data = request.get_json()
    solicitud_id = data.get('sid')
    response = data.get('response')
    estudiante_id = session.get('usuario_id')
    
    if not solicitud_id or response not in ('aceptada', 'rechazada'):
        return jsonify({'status': 'failed', 'error': 'Invalid params'}), 404

    solicitud = SolicitudVinculacion.query.filter_by(id=solicitud_id, estudiante_id=estudiante_id).order_by(desc(SolicitudVinculacion.fecha_solicitud)).first()
    

    if not solicitud:
        return jsonify({'status': 'failed', 'error': 'Request not found'}), 404
    
    solicitud.estado = response

    if response == 'aceptada':
        relacion = SupervisorEstudiante(
            supervisor_id=solicitud.supervisor_id,
            estudiante_id=solicitud.estudiante_id
        )
        db.session.add(relacion)
    
    else:
        solicitud.estado = 'rechazada'

    notificacion = (
        Notificaciones.query
        .filter(
            Notificaciones.usuario_id == estudiante_id,
            Notificaciones.notificacion.like(f'%acciones-{solicitud_id}%')
        )
        .first()
    )

    if notificacion:
        import re
        notificacion.notificacion = re.sub(
            rf'<span id="acciones-{solicitud_id}".*?</span>',
            '',
            notificacion.notificacion,
            flags=re.DOTALL
        )
        
    s_correo = solicitud.supervisor.correo
    enviar_notificacion_respuesta_lr(s_correo, response, estudiante_id)

    db.session.commit()
    
    return jsonify({'status': 'success', 'response': response}), 201

@relaciones_bp.route('/link_request')
@supervisor_required
def view_link_request():
    return render_template("/s_link_request.html")

@relaciones_bp.route('/link_request', methods=['POST']) # envía solicitud de vinculación escribiendo datos en tabla solicitud_vinculacion
@supervisor_required
def send_link_request():
    supervisor_id = session.get('supervisor_id')
    email = request.form['email']

    try:
        UserService.get_from_email(email)
        student_id = UserRepository.get_id_by_email(email)
        LinkRequestService.link_request(supervisor_id, student_id)
        send_link_request_notification(supervisor_id, student_id)
        flash(f'Link request sent to {email}', 'success')
        return redirect(url_for('relaciones.send_link_request'))
    
    except ValueError as e:
        flash(f'Operation failed: {str(e)}', 'error')
        return redirect(url_for('relaciones.send_link_request'))
        