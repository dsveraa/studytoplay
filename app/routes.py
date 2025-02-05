from flask import render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import desc

from app.models import Estudio, Tiempo, Uso, Usuario, Asignatura
from . import db

import time
import threading

ms = 0
sec = 0
min = 0
hr = 0
running = False
stop_event = threading.Event()

def start_timer():
    global ms, sec, min, hr, running
    if running:
        return
    
    running = True
    stop_event.clear()
    count = 0

    while not stop_event.is_set():
        time.sleep(0.01)
        ms += 1

        if ms == 100:
            ms = 0
            sec += 1

        if sec == 60:
            sec = 0
            min += 1

        if min == 60:
            min = 0
            hr += 1

        count += 1
        if count % 500 == 0:
            print(f"{hr:02}:{min:02}:{sec:02}.{ms:02}")

def stop_timer():
    global running, ms, sec, min, hr
    running = False
    stop_event.set()
    ms = 0
    sec = 0
    min = 0
    hr = 0
    print("Reloj detenido.")

def register_routes(app):

    @app.route('/start_clock')
    def start_clock():
        global running
        if not running:
            timer_thread = threading.Thread(target=start_timer, daemon=True)
            timer_thread.start()
        return jsonify({"message": "Timer started"})

    @app.route('/get_time')
    def get_time():
        global running, ms, sec, min, hr
        return jsonify({"hr": hr, "min": min, "sec": sec, "ms": ms})
     
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

    @app.route("/use_time")
    def use_time():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session.get("usuario_id")
        tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        tiempo_valor = tiempo.tiempo if tiempo else 0

        if request.method == 'POST':
            data = request.get_json()
            
            start = data.get('start')
            end = data.get('end')
            time = data.get('time')
            
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
            tiempo.tiempo = time
            db.session.add(tiempo)

            db.session.commit()
            return jsonify({'redirect': url_for('perfil')})
        
        return render_template("use_time.html", tiempo=tiempo_valor)      

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
        
        return render_template("perfil.html", id=usuario_id, nombre=usuario_nombre, estudios=estudios)

    @app.route("/logout")
    def logout():
        session.pop("usuario_id", None)
        session.pop("usuario_nombre", None)
        return redirect(url_for("home"))

    @app.route("/")
    def home():
        return render_template("login.html")
