from flask import flash, render_template, request, redirect, url_for, session, jsonify, Blueprint
from sqlalchemy import desc

from app.models import Estudio, Asignatura
from app.repositories.subject_repository import SubjectRepository
from app.services.subject_service import SubjectService
from app.services.user_service import UserService, UserStatusService
from app.utils.helpers import login_required, revisar_nuevas_notificaciones

from .. import db


academico_bp = Blueprint('academico', __name__)

@academico_bp.route('/switch_status/<status>/', methods=['POST'])
@login_required
def switch_status(status: str):
    user_id = UserService.get_id_from_session()
    current_status = UserStatusService.switch_status(user_id, status)
    return jsonify({
        'status': current_status.estado
    }), 200

    
@academico_bp.route('/edit_record/<id>', methods=["GET", "POST"])
def edit_record(id):
    usuario_id = session.get("usuario_id")
    summary_obj = Estudio.query.filter_by(id=id, usuario_id=usuario_id).first()
    summary = summary_obj.resumen

    if request.method == 'POST':
        data = request.get_json()
        summary = data.get('summary')
        summary_obj.resumen = summary
        db.session.commit()
        return redirect(url_for("core.perfil"))

    return render_template("edit_record.html", summary=summary)



@academico_bp.route("/records")
@academico_bp.route("/records/<activity_id>")
def records(activity_id=None):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    usuario_id = session.get("usuario_id")
    asignaturas_obj = Asignatura.query.filter_by(usuario_id=usuario_id).all()

    if activity_id:
        activity_obj = Estudio.query.filter_by(usuario_id=usuario_id, asignatura_id=activity_id).order_by(desc(Estudio.id)).all()
        nombre_asignatura_obj = Asignatura.query.filter_by(id=activity_id).first()
        nombre_asignatura = nombre_asignatura_obj.nombre if nombre_asignatura_obj else "Desconocida"
    else:
        activity_obj = Estudio.query.filter_by(usuario_id=usuario_id).order_by(desc(Estudio.id)).limit(20).all()
        nombre_asignatura = "Latest"
    
    revisar_nuevas_notificaciones(usuario_id)
    
    return render_template("records.html", 
                            estudios=activity_obj, 
                            asignaturas=asignaturas_obj, 
                            nombre_asignatura=nombre_asignatura
                            )


@academico_bp.route("/subject")
def subjects_management():
    user_id = UserService.get_id_from_session()
    subjects = SubjectRepository.get_all_subjects_by_user_id(user_id)
    subjects_list = SubjectService.transform_obj_subject_to_list(subjects)

    return render_template('subjects.html', subjects=subjects_list)


@academico_bp.route("/subject", methods=['POST'])
def add_subject():
    data = request.get_json()
    subject = data.get('subject')

    user_id = UserService.get_id_from_session()
    new_subject = SubjectService.add_subject(user_id, subject)
    print(new_subject)
    flash(f'New subject added: <b>{new_subject.nombre}</b>', 'success')    
    return jsonify({"status": "ok", "subject": new_subject.nombre}), 201



@academico_bp.route("/subject", methods=['PUT'])
def edit_subject():
    data = request.get_json()
    new_name = data.get('subject')
    subject_id = data.get('subject_id')
    
    user_id = UserService.get_id_from_session()
    
    try:
        result = SubjectService.edit_subject(user_id, subject_id, new_name)
        return jsonify({
            'status': 'ok',
            'new_name': result
        }), 200
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

    
@academico_bp.route("/subject", methods=['DELETE'])
def delete_subject():
    data = request.get_json()
    subject_id = data.get('subject_id')
    
    user_id = UserService.get_id_from_session()
    
    try:
        result = SubjectService.delete_subject(user_id, subject_id)
        return jsonify({
            'status': 'ok',
            'new_name': result
        }), 204
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
