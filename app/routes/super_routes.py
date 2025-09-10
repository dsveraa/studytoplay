import logging
from flask import flash, jsonify, render_template, request, redirect, url_for, Blueprint
from sqlalchemy import desc

from app.models import Estudio, Uso, Asignatura, RegistroNotas, Settings
from app.services.settings_service import UserSettings
from app.services.time_service import UserTime
from app.utils.ms_to_hms import ms_to_hms
from app.utils.debugging_utils import printn
from app.utils.helpers import relation_required, supervisor_required, listar_asignaturas, listar_registro_notas, id_from_json, id_from_kwargs
from app.services.notifications_service import Notification, NotificationRepository
from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive, get_currency_data

from .. import db


super_bp = Blueprint('super', __name__)

@super_bp.route('/student_info/<id>', methods=['GET'])
@supervisor_required
@relation_required(id_from_kwargs)
def student_info(id):
    
    activity_obj = Estudio.query.filter_by(usuario_id=id).order_by(desc(Estudio.id)).limit(5).all()
    use_obj = Uso.query.filter_by(usuario_id=id).order_by(desc(Uso.id)).limit(10).all()

    return render_template("s_records.html", estudios=activity_obj, usos=use_obj)

@super_bp.route('/grade_record/<id>', methods=["GET"])
@supervisor_required
@relation_required(id_from_kwargs)
def grade_record(id):
    asignaturas = listar_asignaturas(id)
    registro_notas = listar_registro_notas(id)

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(id, repo)
    best_grades = grade_incentive.filter_grades()

    return render_template('s_grade_record.html', asignaturas=asignaturas, registro_notas=registro_notas, best_grades=best_grades)

@super_bp.route("/grade_record/warning/<int:id>")
@supervisor_required
@relation_required(id_from_kwargs)
def grade_record_warning(id):
    return f"<h3>You must set at least 1 incentive in <a href='/settings/{id}'>Settings</a>.</h3>"

@super_bp.route('/grade_record/<id>', methods=['POST'])
@supervisor_required
@relation_required(id_from_kwargs)
def add_grade_record(id):
    data = request.get_json()
    
    asignatura = data.get('asignatura')
    tema = data.get('tema')
    nota = data.get('nota')
    fecha = data.get('fecha')

    registro_notas = RegistroNotas(
        usuario_id=id,
        asignatura_id=asignatura,
        tema=tema,
        nota=nota,
        fecha=fecha,
        )
    db.session.add(registro_notas)
    db.session.commit()

    asignatura_nombre = Asignatura.query.get(asignatura).nombre

    amount, currency, symbol = get_currency_data(id, nota)

    repo = NotificationRepository(db.session)
    notification = Notification(id, repo)
    notification.notify_grade(nota, asignatura_nombre, 'add', amount, currency, symbol)

    return redirect(url_for("super.grade_record", id=id))  
    
@super_bp.route("/payment", methods=["PUT"])
@supervisor_required
def mark_paid():
    data = request.get_json()
    registro_id = data.get('grade_to_pay')
    estudiante_id = data.get('estudiante_id')
    
    registro = RegistroNotas.query.get_or_404(registro_id)
    nota = registro.nota
    logging.info(f"registro nota: {nota}")
    asignatura = registro.asignatura.nombre
    
    amount, currency, symbol = get_currency_data(estudiante_id, nota)
    logging.info(f"amount: {amount}")

    if amount == None:
        flash("An unexpected error occurred, please try again.", "error")
        return redirect(url_for("super.grade_record", id=estudiante_id))
        
    registro.estado = True
    db.session.commit()

    repo = NotificationRepository(db.session)
    notification = Notification(estudiante_id, repo)
    notification.notify_grade(nota, asignatura, 'pay', amount, currency, symbol)
    
    flash("The payment has been recorded successfully", "success")
    return redirect(url_for("super.grade_record", id=estudiante_id))

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
def time_information(id):
    user_time = UserTime(id)
    current_time = user_time.get_time()

    return render_template("s_time.html", current_time=current_time, user_id=id)

@super_bp.route("/s_time/<int:id>/<action>", methods=["PUT"])
@supervisor_required
def manage_time(id, action):
    data = request.get_json()
    time = data.get("time")
    
    user_time = UserTime(id)
    current_time = user_time.get_time()
    previous_time = ms_to_hms(current_time)
    new_time = user_time.manage_time(action, time)
    
    flash(f"Time updated, previous time: <b>{previous_time}</b>", "success")
    return jsonify({"new_time": new_time, "previous_time": current_time}), 200
