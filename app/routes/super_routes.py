from flask import flash, jsonify, render_template, request, redirect, url_for, Blueprint

from app.models import Asignatura
from app.repositories.record_repository import RecordRepository
from app.repositories.time_repository import TimeRepository
from app.services.academic_service import AcademicService
from app.services.settings_service import UserSettings
from app.services.time_service import UserTime
from app.services.user_service import UserService
from app.utils.ms_to_hms import ms_to_hms
from app.utils.debugging_utils import printn
from app.utils.helpers import relation_required, supervisor_required, listar_asignaturas, listar_registro_notas, id_from_json, id_from_kwargs
from app.services.notifications_service import Notification, NotificationRepository
from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive, get_currency_data

from .. import db


super_bp = Blueprint('super', __name__)

@super_bp.route('/student_records/<id>')
@supervisor_required
@relation_required(id_from_kwargs)
def student_records(id):
    name = UserService.get_username_by_id(id)
    activity_obj = RecordRepository.get_records_list(id, 5)
    use_obj = TimeRepository.get_use_obj(id, 10)

    return render_template("s_records.html", estudios=activity_obj, usos=use_obj, name=name)

@super_bp.route('/grade_incentive/<id>')
@supervisor_required
@relation_required(id_from_kwargs)
def grade_incentive(id):
    asignaturas = listar_asignaturas(id)
    registro_notas = listar_registro_notas(id)

    user_settings = UserSettings(id)
    name = user_settings.name

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(id, repo)
    best_grades = grade_incentive.filter_grades()

    return render_template('s_grade_incentive.html', asignaturas=asignaturas, registro_notas=registro_notas, best_grades=best_grades, name=name, user_id=id)

@super_bp.route("/grade_incentive/warning/<int:id>")
@supervisor_required
@relation_required(id_from_kwargs)
def grade_incentive_warning(id):
    flash(f"You must set at least 1 incentive in <a href='/settings/{id}'>Settings</a>", 'warning')
    return redirect(url_for('core.home'))

@super_bp.route('/grade_incentive/<id>', methods=['POST'])
@supervisor_required
@relation_required(id_from_kwargs)
def add_grade_incentive(id):
    data = request.get_json()

    asignatura_id = data.get('asignatura')
    tema = data.get('tema')
    nota = data.get('nota')
    fecha = data.get('fecha')

    AcademicService.add_grade(id, asignatura_id, tema, nota, fecha)
    asignatura_nombre = Asignatura.query.get(asignatura_id).nombre
    amount, currency, symbol = get_currency_data(id, nota)
    repo = NotificationRepository(db.session)
    notification = Notification(id, repo)
    notification.notify_grade(nota, asignatura_nombre, 'add', amount, currency, symbol)

    flash_msg = f"A new grade has been submited. Subject: <b>{asignatura_nombre}</b>, grade: <b>{nota}</b>"
    return jsonify({"flash": {"message": flash_msg, "category": "success"}})

    
@super_bp.route("/payment", methods=["PUT"])
@supervisor_required
def mark_paid():
    data = request.get_json()
    record_id = data.get('grade_to_pay')
    student_id = data.get('estudiante_id')
    
    grade, subject = AcademicService.get_grade_and_subject(record_id)
    amount, currency, symbol = get_currency_data(student_id, grade)

    AcademicService.set_grade_as_paid(record_id)

    repo = NotificationRepository(db.session)
    notification = Notification(student_id, repo)
    notification.notify_grade(grade, subject, 'pay', amount, currency, symbol)
    
    flash("The payment has been recorded successfully", "success")
    return redirect(url_for("super.grade_incentive", id=student_id))

@super_bp.route("/trophy/<int:id>", methods=["POST"])
@supervisor_required
@relation_required(id_from_kwargs)
def set_trophy(id):
    reward = request.form.get("reward", "").strip()
    user_settings = UserSettings(id)

    if not reward:
        flash("Isn't possible to submit empty data as a Trophy.", "warning")
        return redirect(url_for("core.settings", id=id))

    user_settings.set_trophy(reward)
    flash(f"A new trophy has been set up: <b>{reward}</b>", "success")
    return redirect(url_for("core.settings", id=id))

@super_bp.route("/extra_time/<int:id>/<int:extra_time>", methods=["PUT"])
@supervisor_required
@relation_required(id_from_kwargs)
def set_extra_time(id, extra_time):
    user_settings = UserSettings(id)
    user_settings.set_extra_time(extra_time)
    return jsonify({"status": "success"}), 200

@super_bp.route("/study_fun_ratio/<int:id>/<ratio>", methods=["PUT"])
@supervisor_required
@relation_required(id_from_kwargs)
def set_study_fun_ratio(id, ratio):
    user_settings = UserSettings(id)
    user_settings.set_study_fun_ratio(ratio)
    return jsonify({"status": "success"}), 200

@super_bp.route("/s_time/<int:id>")
@supervisor_required
@relation_required(id_from_kwargs)
def time_information(id):
    user_time = UserTime(id)
    current_time = user_time.get_time()
    settings = UserSettings(id)
    name = settings.name
    return render_template("s_time.html", current_time=current_time, user_id=id, name=name)

@super_bp.route("/s_time", methods=["PUT"])
@supervisor_required
@relation_required(id_from_json)
def manage_time():
    data = request.get_json()
    time = data.get("time")
    id = data.get("estudiante_id")
    action = data.get("action")
    user_time = UserTime(id)
    current_time = user_time.get_time()
    previous_time = ms_to_hms(current_time)
    new_time = user_time.manage_time(action, time)
    
    flash(f"Time updated, previous time: <b>{previous_time}</b>", "success")
    return jsonify({"new_time": new_time, "previous_time": current_time}), 200

@super_bp.route("/s_time/reset", methods=["PUT"])
@supervisor_required
@relation_required(id_from_json)
def reset_time():
    data = request.get_json()
    id = data.get("estudiante_id")
    user_time = UserTime(id)
    current_time = user_time.get_time()
    previous_time = ms_to_hms(current_time)
    reset = user_time.reset_time()

    flash(f"The time has been reset. Previous time <b>{previous_time}</b>", "success")
    return jsonify({"new_time": reset, "previous_time": current_time}), 201
