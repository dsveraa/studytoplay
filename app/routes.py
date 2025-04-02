from flask import render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import desc

from app.models import Estudio, Tiempo, Uso, Usuario, Asignatura, AcumulacionTiempo
from app.utils.helpers import asignar_estrellas, asignar_nivel, asignar_trofeos, crear_plantilla_estrellas, mostrar_estrellas, mostrar_trofeos, porcentaje_tiempos, sumar_tiempos, mostrar_nivel
from . import db


from pprint import pprint
from typing import List, Tuple, Dict

from decouple import config

SECRET_KEY = config('SECRET_KEY')

def register_routes(app):
    @app.route('/edit_record/<id>', methods=["GET", "POST"])
    def edit_record(id):
        usuario_id = session.get("usuario_id")
        summary_obj = Estudio.query.filter_by(id=id, usuario_id=usuario_id).first()
        summary = summary_obj.resumen

        if request.method == 'POST':
            data = request.get_json()
            summary = data.get('summary')
            summary_obj.resumen = summary
            db.session.commit()
            return redirect(url_for("perfil"))

        return render_template("edit_record.html", summary=summary)

    @app.route('/get_time')
    def get_time():
        current_time = datetime.now()
        return jsonify({'current_time': current_time})
         
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
        return redirect(url_for('perfil'))

    @app.route("/add_time", methods=["GET", "POST"])
    def add_time():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
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
            
            if tiempo:
                tiempo.tiempo += time
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
            asignar_estrellas(usuario_id)
            asignar_nivel(usuario_id)
            asignar_trofeos(usuario_id)
            

            return jsonify({'redirect': url_for('perfil')})
        
        return render_template("add_time.html", asignaturas=asignaturas)

    @app.route("/use_time", methods=["GET", "POST"])
    def use_time():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
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

            # print(start, end, time)
            
            usuario_id = session.get("usuario_id")

            fecha_inicio = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            fecha_fin = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

            uso = Uso(
                usuario_id=usuario_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                actividad=activity or "Sin especificar"
            )
            db.session.add(uso)
            
            tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
            tiempo.tiempo = time
            db.session.add(tiempo)

            db.session.commit()
            ultimo_uso = Uso.query.order_by(Uso.id.desc()).first()
            print("Último uso registrado:", ultimo_uso.__dict__)
            
            return jsonify({'redirect': url_for('perfil')})
        
        return render_template("use_time.html", username=username, usos=use_obj)

    @app.route("/get_remaining_time")
    def get_remaining_time():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session.get("usuario_id")
        tiempo = Tiempo.query.filter_by(usuario_id=usuario_id).first()
        tiempo_valor = tiempo.tiempo if tiempo else 0
            
        return jsonify({'remaining_time': tiempo_valor})

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
                session.permanent = True
                return redirect(url_for("perfil"))
            else:
                return "Correo o contraseña incorrectos."
        return render_template("login.html")

    @app.route("/records")
    @app.route("/records/<activity_id>")
    def records(activity_id=None):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session.get("usuario_id")
        asignaturas_obj = Asignatura.query.filter_by(usuario_id=usuario_id).all()

        if activity_id:
            activity_obj = Estudio.query.filter_by(usuario_id=usuario_id, asignatura_id=activity_id).order_by(desc(Estudio.id)).all()
            nombre_asignatura_obj = Asignatura.query.filter_by(id=activity_id).first()
            nombre_asignatura = nombre_asignatura_obj.nombre if nombre_asignatura_obj else "Desconocida"
        else:
            activity_obj = Estudio.query.filter_by(usuario_id=usuario_id).order_by(desc(Estudio.id)).limit(20).all()
            nombre_asignatura = "Latest"
        
        return render_template("records.html", 
                               estudios=activity_obj, 
                               asignaturas=asignaturas_obj, 
                               nombre_asignatura=nombre_asignatura
                               )
    
    @app.route("/perfil")
    def perfil():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session["usuario_id"]
        usuario_nombre = session["usuario_nombre"]
        
        estudios = Estudio.query.filter_by(usuario_id=usuario_id).order_by(desc(Estudio.id)).all()

        if not estudios:
            return render_template("perfil.html", id=usuario_id, nombre=usuario_nombre)

        asignaturas_obj = Asignatura.query.filter_by(usuario_id=usuario_id).all()

        asignaturas_nombre = [asignatura.nombre for asignatura in asignaturas_obj]

        datos_estudios = [{
            'fecha_inicio': estudio.fecha_inicio,
            'fecha_fin': estudio.fecha_fin,
            'asignatura': estudio.asignatura.nombre if estudio.asignatura else 'No se seleccionó',
            'asignatura_id': estudio.asignatura_id
            }
            for estudio in estudios]
        
        total_tiempo_asignaturas = {asignatura: sumar_tiempos(datos_estudios, asignatura) for asignatura in asignaturas_nombre}

        tiempo_total = sum(total_tiempo_asignaturas.values(), timedelta())

        porcentajes_asignaturas = {asignatura: f'{porcentaje_tiempos(total_tiempo_asignaturas[asignatura], tiempo_total):.1f}' for asignatura in asignaturas_nombre}

        nivel: int = mostrar_nivel(usuario_id)
        trofeos: int = mostrar_trofeos(usuario_id)
        cantidad_estrellas: int = mostrar_estrellas(usuario_id)
        estrellas: List[int] = crear_plantilla_estrellas(cantidad_estrellas)

        return render_template(
            "perfil.html", 
            id=usuario_id, 
            nombre=usuario_nombre, 
            estudios=estudios, 
            asignaturas=asignaturas_obj, 
            porcentajes_asignaturas=porcentajes_asignaturas,
            nivel=nivel,
            estrellas=estrellas,
            trofeos=trofeos)

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

    