from flask import render_template, request, session, jsonify, Blueprint
from sqlalchemy import desc
from sqlalchemy.orm import aliased

from app.models import Usuario, SolicitudVinculacion, SupervisorEstudiante, Notificaciones
from app.utils.helpers import login_required, supervisor_required, enviar_notificacion_link_request, enviar_notificacion_respuesta_lr

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

@relaciones_bp.route('/link_request', methods=['GET', 'POST']) # envía solicitud de vinculación escribiendo datos en tabla solicitud_vinculacion
@supervisor_required
def link_request(id=None):
    if request.method == 'POST':            
        supervisor_id = session.get('supervisor_id')
        usuario_estudiante = request.form['email']
        
        estudiante_id = db.session.query(Usuario.id).filter_by(correo=usuario_estudiante).scalar()

        if not estudiante_id:
            return jsonify({'status': 'failed', 'error': f"No students were found with the username '{usuario_estudiante}'"})

        estado_solicitud_vinculacion = (
            db.session.query(SolicitudVinculacion.estado)
            .select_from(SolicitudVinculacion)
            .filter_by(supervisor_id=supervisor_id, estudiante_id=estudiante_id)
            .order_by(desc(SolicitudVinculacion.fecha_solicitud))
            .limit(1).scalar()
            )
                    
        relacion_supervisor_estudiante = (
            db.session.query(SupervisorEstudiante)
            .filter_by(supervisor_id=supervisor_id, estudiante_id=estudiante_id)
            .scalar()
        )
        
        if relacion_supervisor_estudiante:
            return '<h1>This supervisor account is already following the student</h1>'

        if estado_solicitud_vinculacion == 'pendiente':
            return '<h1>There is a pending link request for this student</h1>'
            
        else:
            solicitud = SolicitudVinculacion(
                supervisor_id=supervisor_id,
                estudiante_id=estudiante_id,
                estado='pendiente'
            )
            db.session.add(solicitud)
            db.session.commit()

            enviar_notificacion_link_request(supervisor_id, estudiante_id)


        return jsonify({'response': 'solicitud enviada'})
    return render_template("/s_link_request.html")

