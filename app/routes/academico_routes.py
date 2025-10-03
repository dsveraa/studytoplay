from flask import flash, render_template, request, redirect, url_for, session, jsonify, Blueprint

from app.repositories.subject_repository import SubjectRepository
from app.services.record_service import RecordService
from app.services.subject_service import SubjectService
from app.services.user_service import UserService, UserStatusService
from app.utils.helpers import login_required, check_new_notifications


academico_bp = Blueprint('academico', __name__)

@academico_bp.route('/switch_status/<status>/', methods=['POST'])
@login_required
def switch_status(status: str):
    user_id = UserService.get_id_from_session()
    current_status = UserStatusService.switch_status(user_id, status)
    return jsonify({
        'status': current_status.estado
    }), 200

    
@academico_bp.route('/edit_record/<id>')
def view_edit_record(id):
    user_id = UserService.get_id_from_session()
    summary = RecordService.edit_record(id, user_id)
    return render_template("edit_record.html", summary=summary)


@academico_bp.route('/edit_record/<id>', methods=["POST"])
def edit_record(id):
    data = request.get_json()
    summary = data.get('summary')
    user_id = UserService.get_id_from_session()
    RecordService.edit_record(id, user_id, summary)
    return redirect(url_for("core.perfil"))  


@academico_bp.route("/records")
@academico_bp.route("/records/<activity_id>")
def records(activity_id=None):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    user_id = UserService.get_id_from_session()
    asignaturas_obj = SubjectService.get_subject_obj_by_user_id(user_id)
    activity_obj = RecordService.get_activity_obj(user_id, activity_id)
    nombre_asignatura = SubjectService.get_subject_name(activity_id)
    
    check_new_notifications(user_id)
    
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
