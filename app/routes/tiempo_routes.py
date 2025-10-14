from flask import render_template, request, redirect, url_for, session, jsonify, Blueprint
from datetime import datetime

from app.repositories.time_repository import TimeRepository
from app.services.record_service import RecordService
from app.services.subject_service import SubjectService
from app.services.time_service import UserTime
from app.services.user_service import UserService
from app.utils.debugging_utils import printn
from app.utils.helpers import check_new_notifications, format_date


tiempo_bp = Blueprint('tiempo', __name__)

@tiempo_bp.route('/get_time')
def get_time():
    current_time = datetime.now()
    return jsonify({'current_time': current_time})
        

@tiempo_bp.route("/cancel", methods=["GET", "POST"])
def cancel():
    return redirect(url_for('core.perfil'))

@tiempo_bp.route("/add_time")
def add_time_view():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    user_id = UserService.get_id_from_session()

    subjects_obj = SubjectService.get_subject_obj_by_user_id(user_id)
    subjects = [{'id': asignatura.id, 'nombre': asignatura.nombre} for asignatura in subjects_obj]
    
    check_new_notifications(user_id)
    
    return render_template("add_time.html", asignaturas=subjects)


@tiempo_bp.route("/add_time", methods=["POST"])
def add_time():
    data = request.get_json()   
    start = data.get('start')
    end = data.get('end')
    summary = data.get('summary')
    subject_id = data.get('subject_id')
    new_time = data.get('time')
    start_date = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    user_id = UserService.get_id_from_session()

    RecordService.add_study_session(user_id, start_date, end_date, summary, subject_id)
    UserTime.handle_new_time(user_id, new_time)
    
    return jsonify({'redirect': url_for('core.perfil')})
    

@tiempo_bp.route("/use_time")
def use_time_view():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    user_id = session.get("usuario_id")
    username = session.get("usuario_nombre")

    use_obj = TimeRepository.get_sorted_time_uses_list(user_id, 10)

    check_new_notifications(user_id)
    
    return render_template("use_time.html", username=username, usos=use_obj)

@tiempo_bp.route("/use_time", methods=["POST"])
def use_time():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    time = data.get('time')
    activity = data.get('actividad', '').strip()
    
    if not activity:
        return jsonify({'error': "Activity can't be blank"}), 400

    start_date = format_date(start)
    end_date = format_date(end)
    
    user_id = UserService.get_id_from_session()    
    user_time = UserTime(user_id)
    user_time.record_time(time)
    
    TimeRepository.commit()

    time_service = UserTime(user_id)
    remaining_time = time_service.time_obj.tiempo

    UserTime.add_use(user_id, start_date, end_date, activity, remaining_time)    

    return jsonify({'redirect': url_for('core.perfil')})

@tiempo_bp.route("/get_remaining_time")
def get_remaining_time():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    user_id = UserService.get_id_from_session()
    time = TimeRepository.get_time_object(user_id)
    time_value = time.tiempo if time else 0
        
    return jsonify({'remaining_time': time_value}), 200
