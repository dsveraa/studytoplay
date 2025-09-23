from venv import logger
from flask import render_template, request, redirect, url_for, session, jsonify, Blueprint
from datetime import datetime
from sqlalchemy import desc

from app.models import Estudio, Tiempo, Uso, Asignatura, AcumulacionTiempo
from app.services.settings_service import UserSettings
from app.utils.helpers import revisar_nuevas_notificaciones

from .. import db


tiempo_bp = Blueprint('tiempo', __name__)

@tiempo_bp.route('/get_time')
def get_time():
    current_time = datetime.now()
    return jsonify({'current_time': current_time})
        
@tiempo_bp.route("/update_time", methods=["POST"])
def update_time():
    data = request.get_json()
    time = data.get('time')
    
    usuario_id = session.get("usuario_id")
    
    tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
    tiempo.tiempo = time
    db.session.add(tiempo)
    db.session.commit()
    return "tiempo actualizado en el servidor..."      

@tiempo_bp.route("/cancel", methods=["GET", "POST"])
def cancel():
    return redirect(url_for('core.perfil'))

@tiempo_bp.route("/add_time", methods=["GET", "POST"])
def add_time():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    usuario_id = session.get("usuario_id")

    asignaturas_obj = Asignatura.query.filter_by(usuario_id=usuario_id).all()
    asignaturas = [{'id': asignatura.id, 'nombre': asignatura.nombre} for asignatura in asignaturas_obj]
    
    if request.method == 'POST':

        data = request.get_json()
        
        start = data.get('start')
        end = data.get('end')
        summary = data.get('summary')
        time = data.get('time')
        subject_id = data.get('subject_id')
        
        fecha_inicio = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        fecha_fin = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

        estudio = Estudio(
            usuario_id=usuario_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            resumen=summary,
            asignatura_id=subject_id
        )
        db.session.add(estudio)
        
        tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        acumulacion_tiempo = AcumulacionTiempo.query.filter_by(usuario_id=usuario_id).first()
        
        user_settings = UserSettings(usuario_id)
        multiplicador = user_settings.get_study_fun_ratio()
        
        if tiempo:
            tiempo.tiempo += (time * multiplicador) # temporal, multiplicador de tiempo 
        else:
            tiempo = Tiempo(usuario_id=usuario_id, tiempo=time)
            db.session.add(tiempo)
        
        if acumulacion_tiempo:
            acumulacion_tiempo.cantidad += time
        else:
            acumulacion_tiempo = AcumulacionTiempo(usuario_id=usuario_id, cantidad=time)
            db.session.add(acumulacion_tiempo)

        db.session.commit()
        db.session.refresh(acumulacion_tiempo)
        
        return jsonify({'redirect': url_for('core.perfil')})
    
    revisar_nuevas_notificaciones(usuario_id)
    
    return render_template("add_time.html", asignaturas=asignaturas)

@tiempo_bp.route("/use_time", methods=["GET", "POST"])
def use_time():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    usuario_id = session.get("usuario_id")
    username = session.get("usuario_nombre")

    use_obj = Uso.query.filter_by(usuario_id=usuario_id).order_by(desc(Uso.id)).limit(10).all()

    if request.method == 'POST':
        data = request.get_json()
        print("datos recibidos:", data)
        start = data.get('start')
        end = data.get('end')
        time = data.get('time')
        activity = data.get('actividad', '').strip()
        if not activity:
            return jsonify({'error': 'La actividad no puede estar vacía'}), 400

        usuario_id = session.get("usuario_id")
        
        tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        tiempo.tiempo = time
        db.session.add(tiempo)
        db.session.commit()

        fecha_inicio = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        fecha_fin = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

        time_obj = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        remaining_time = time_obj.tiempo

        uso = Uso(
            usuario_id=usuario_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            actividad=activity or "Sin especificar",
            remaining_time=remaining_time
        )
        db.session.add(uso)
        db.session.commit()

        ultimo_uso = Uso.query.order_by(Uso.id.desc()).first()
        logger.info("Último uso registrado:", ultimo_uso.__dict__)
        
        return jsonify({'redirect': url_for('core.perfil')})
    
    revisar_nuevas_notificaciones(usuario_id)
    
    return render_template("use_time.html", username=username, usos=use_obj)

@tiempo_bp.route("/get_remaining_time")
def get_remaining_time():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    usuario_id = session.get("usuario_id")
    tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
    tiempo_valor = tiempo.tiempo if tiempo else 0
        
    return jsonify({'remaining_time': tiempo_valor})
