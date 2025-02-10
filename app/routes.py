from flask import render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import desc

from app.models import Estudio, Tiempo, Uso, Usuario, Asignatura
from app.utils.helpers import porcentaje_tiempos, sumar_tiempos
from . import db

import time
import threading

from pprint import pprint

class Timer:
    def __init__(self):
        self.ms = 0
        self.sec = 0
        self.min = 0
        self.hr = 0
        self.running = False
        self.stop_event = threading.Event()

timer = Timer()

def start_timer():
    if timer.running:
        return
    
    timer.running = True
    timer.stop_event.clear()
    count = 0

    while not timer.stop_event.is_set():
        time.sleep(0.01)
        timer.ms += 1

        if timer.ms == 100:
            timer.ms = 0
            timer.sec += 1

        if timer.sec == 60:
            timer.sec = 0
            timer.min += 1

        if timer.min == 60:
            timer.min = 0
            timer.hr += 1

        count += 1
        if count % 500 == 0:
            print(f"{timer.hr:02}:{timer.min:02}:{timer.sec:02}.{timer.ms:02}")

def stop_timer():
    timer.running = False
    timer.stop_event.set()
    timer.ms = 0
    timer.sec = 0
    timer.min = 0
    timer.hr = 0
    print("Reloj detenido.")

def convertir_milisegundos(ms):
    hr = ms // 3600000
    ms %= 3600000
    min = ms // 60000
    ms %= 60000
    sec = ms // 1000
    ms %= 1000
    return hr, min, sec, ms

def register_routes(app):
    @app.route('/stamp_time')
    def start_countdown():
        session["start_time"] = datetime.now()
        return jsonify({'message': 'se inició la cuenta regresiva'})
    
    @app.route('/redeem_time')
    def redeem_time():
        time_now = datetime.now()
        start_time = session.get("start_time")
        time_difference = (time_now - start_time.replace(tzinfo=None)).total_seconds() * 1000
        updated_time = str(session["initial_time"] - time_difference)
        print('updated_time:', type(updated_time), 'value=', updated_time)
        return jsonify({'updated_time': updated_time})
    
    @app.route('/start_clock')
    def start_clock():
        if not timer.running:
            timer_thread = threading.Thread(target=start_timer, daemon=True)
            timer_thread.start()
        return jsonify({"message": "Timer started"})

    @app.route('/get_time')
    def get_time():
        return jsonify({
            "hr": timer.hr,
            "min": timer.min,
            "sec": timer.sec,
            "ms": timer.ms
        })
     
    @app.route("/update_time", methods=["POST"])
    def update_time():
        data = request.get_json()
        time = data.get('time')
        
        usuario_id = session.get("usuario_id")
        
        tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        tiempo.tiempo = time
        db.session.add(tiempo)
        db.session.commit()
        return "tiempo actualizado en el servidor..."      

    @app.route("/cancel", methods=["GET", "POST"])
    def cancel():
        stop_timer()
        return redirect(url_for('perfil'))

    @app.route("/add_time", methods=["GET", "POST"])
    def add_time():
        asignaturas_obj = Asignatura.query.all()
        asignaturas = [{'id': asignatura.id, 'nombre': asignatura.nombre} for asignatura in asignaturas_obj]
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        if request.method == 'POST':
            stop_timer()

            data = request.get_json()
            
            start = data.get('start')
            end = data.get('end')
            summary = data.get('summary')
            time = data.get('time')
            subject_id = data.get('subject_id')
            
            usuario_id = session.get("usuario_id")

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
            
            if tiempo:
                    tiempo.tiempo += time
            else:
                tiempo = Tiempo(
                    usuario_id=usuario_id,
                    tiempo=time
                )
                db.session.add(tiempo)

            db.session.commit()
            return jsonify({'redirect': url_for('perfil')})
        
        return render_template("add_time.html", asignaturas=asignaturas)

    @app.route("/use_time", methods=["GET", "POST"])
    def use_time():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session.get("usuario_id")
        username = session.get("usuario_nombre")
        tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        tiempo_valor = tiempo.tiempo if tiempo else 0

        session["initial_time"] = tiempo_valor

        if request.method == 'POST':
            data = request.get_json()
            
            start = data.get('start')
            end = data.get('end')
            time = data.get('time')

            print(start, end, time)
            
            usuario_id = session.get("usuario_id")

            fecha_inicio = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            fecha_fin = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

            uso = Uso(
                usuario_id=usuario_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )
            db.session.add(uso)
            
            tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
            print("hola")
            tiempo.tiempo = time
            db.session.add(tiempo)

            db.session.commit()
            return jsonify({'redirect': url_for('perfil')})
        
        return render_template("use_time.html", tiempo=tiempo_valor, username=username)      

    @app.route("/registro", methods=["GET","POST"])
    def registro():
        if request.method == 'POST':
            nombre = request.form["nombre"]
            email = request.form["email"]
            contrasena = request.form["contrasena"]
            repetir_contrasena = request.form["repetir_contrasena"]
            
            if contrasena != repetir_contrasena:
                return "Las contraseñas no coinciden, intenta nuevamente."
            
            if Usuario.query.filter_by(correo=email).first():
                return "El correo ya está registrado, intenta con otro."
            
            contrasena_hash = generate_password_hash(contrasena)
            
            nuevo_usuario = Usuario(nombre=nombre, correo=email, contrasena=contrasena_hash)
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            return redirect(url_for("login"))
        return render_template("registro.html")
        
    @app.route("/usuarios")
    def mostrar_usuarios():
        usuarios = Usuario.query.all()
        return '<br>'.join([f'{usuario.nombre} ({usuario.correo})' for usuario in usuarios])

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            correo = request.form["correo"]
            contrasena = request.form["contrasena"]
            
            usuario = Usuario.query.filter_by(correo=correo).first()
            
            if usuario and check_password_hash(usuario.contrasena, contrasena):
                session["usuario_id"] = usuario.id
                session["usuario_nombre"] = usuario.nombre
                return redirect(url_for("perfil"))
            else:
                return "Correo o contraseña incorrectos."
        return render_template("login.html")

    @app.route("/perfil")
    def perfil():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session["usuario_id"]
        usuario_nombre = session["usuario_nombre"]
        
        estudios = Estudio.query.filter_by(usuario_id=usuario_id).order_by(desc(Estudio.id)).all()

        asignaturas = Asignatura.query.all()

        asignaturas = [asignatura.nombre for asignatura in asignaturas]

        datos_estudios = [{
            'fecha_inicio': estudio.fecha_inicio,
            'fecha_fin': estudio.fecha_fin,
            'asignatura': estudio.asignatura.nombre if estudio.asignatura else 'No se seleccionó',
            'asignatura_id': estudio.asignatura_id
            }
            for estudio in estudios]
        
        total_tiempo_asignaturas = {asignatura: sumar_tiempos(datos_estudios, asignatura) for asignatura in asignaturas}

        tiempo_total = sum(total_tiempo_asignaturas.values(), timedelta())

        porcentajes_asignaturas = {asignatura: f'{porcentaje_tiempos(total_tiempo_asignaturas[asignatura], tiempo_total):.1f}' for asignatura in asignaturas}

        return render_template(
            "perfil.html", 
            id=usuario_id, 
            nombre=usuario_nombre, 
            estudios=estudios, 
            asignaturas=asignaturas, 
            porcentajes_asignaturas=porcentajes_asignaturas)

    @app.route("/logout")
    def logout():
        session.pop("usuario_id", None)
        session.pop("usuario_nombre", None)
        return redirect(url_for("home"))

    @app.route("/")
    def home():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        return redirect(url_for("perfil"))
