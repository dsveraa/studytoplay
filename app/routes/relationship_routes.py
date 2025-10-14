from flask import flash, redirect, render_template, request, session, jsonify, Blueprint, url_for
from sqlalchemy import desc

from app.models import Usuario, SolicitudVinculacion, SupervisorEstudiante, Notificaciones # no eliminar, para que pasen los tests
from app.repositories.user_repository import UserRepository
from app.services.link_request_service import LinkRequestService
from app.services.notifications_service import Notification
from app.services.relationship_service import RelationsService
from app.services.user_service import UserService
from app.utils.helpers import login_required, supervisor_required, send_link_request_notification, enviar_notificacion_respuesta_lr

from .. import db # no eliminar, para que pasen los tests


relaciones_bp = Blueprint('relaciones', __name__)

@relaciones_bp.route('/received_requests')
@login_required
def received_requests():
    query = RelationsService.get_supervisor_student_relation()
    
    relation_request = [
        {
            'supervisor_id': sid,
            'supervisor': supervisor,
            'estudiante_id': eid,
            'estudiante': student,
            'estado': status,
            'fecha_solicitud': date
        }
        for sid, supervisor, eid, student, status, date in query
    ]

    if not query:
        return jsonify({'status': 'error', 'error': 'query not found'}), 400

    return jsonify({'status': 'ok', 'current_requests': relation_request})

@relaciones_bp.route('/request_response', methods=['POST'])
@login_required
def request_response():
    data = request.get_json()
    request_id = data.get('sid')
    response = data.get('response')
    student_id = session.get('usuario_id')
    
    try:
        link_request = RelationsService.get_link_request(request_id, student_id, response)
    
    except ValueError as e:
        return jsonify({'status': 'failed', 'error': str(e)}), 404   
    
    Notification.delete_link_request_icons(student_id, request_id)
        
    s_mail = link_request.supervisor.correo
    enviar_notificacion_respuesta_lr(s_mail, response, student_id)

    return jsonify({'status': 'success', 'response': response}), 201

@relaciones_bp.route('/link_request')
@supervisor_required
def view_link_request():
    return render_template("/s_link_request.html")

@relaciones_bp.route('/link_request', methods=['POST'])
@supervisor_required
def send_link_request():
    supervisor_id = session.get('supervisor_id')
    email = request.form['email']

    try:
        UserService.get_from_email(email)
        student_id = UserRepository.get_id_by_email(email)
        LinkRequestService.make_link_request(supervisor_id, student_id)
        send_link_request_notification(supervisor_id, student_id)
        flash(f'Link request sent to {email}', 'success')
        return redirect(url_for('relaciones.send_link_request'))
    
    except ValueError as e:
        flash(f'Operation failed: {str(e)}', 'error')
        return redirect(url_for('relaciones.send_link_request'))
