from flask import render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import desc, and_
from sqlalchemy.orm import aliased


from app.models import Estudio, Tiempo, Uso, Usuario, Asignatura, AcumulacionTiempo, Rol, SolicitudVinculacion, SupervisorEstudiante, EstadoUsuario, NuevaNotificacion, Notificaciones, RegistroNotas

from app.utils.helpers import asignar_estrellas, asignar_nivel, asignar_trofeos, crear_plantilla_estrellas, mostrar_estrellas, mostrar_trofeos, porcentaje_tiempos, sumar_tiempos, mostrar_nivel, login_required, supervisor_required, revisar_nuevas_notificaciones, enviar_notificacion_link_request, enviar_notificacion_respuesta_lr, listar_asignaturas, listar_registro_notas

from app.utils.notifications import Notification, NotificationRepository

from . import db


from pprint import pprint
from typing import List, Tuple, Dict
from app.utils.debugging import printn

from decouple import config

from user_agents import parse
import logging

SECRET_KEY = config('SECRET_KEY')

def register_routes(app):
    @app.template_filter('ms_to_hms')
    def ms_to_hms_filter(ms):
        import datetime
        if not ms:
            segundos = 0
        else:
            segundos = ms // 1000
        return str(datetime.timedelta(seconds=segundos))
    
    @app.route('/student_info/<id>', methods=['GET'])
    @supervisor_required
    def student_info(id):
        supervisor_id = session.get('usuario_id')
        relation = SupervisorEstudiante.query.filter_by(supervisor_id=supervisor_id, estudiante_id=id).first()

        if not relation:
            return "Relation not found"
        
        activity_obj = Estudio.query.filter_by(usuario_id=id).order_by(desc(Estudio.id)).limit(5).all()
        use_obj = Uso.query.filter_by(usuario_id=id).order_by(desc(Uso.id)).limit(10).all()

        return render_template("s_records.html", estudios=activity_obj, usos=use_obj)

    @app.route('/log_click', methods=['POST'])
    def log_click():
        data = request.json
        boton = data.get('boton', 'desconocido')
        origen = request.referrer or 'origen desconocido'
        # hora_cliente = data.get('hora_cliente', 'hora no enviada')
        
        ua_strig = request.headers.get('User-Agent', '')
        user_agent = parse(ua_strig)

        navegador = user_agent.browser.family or 'navegador desconocido'
        sistema = user_agent.os.family or 'SO desconocido'

        logging.info(f'Click en: "{boton}", desde "{origen}", usando "{navegador}", en "{sistema}"' )
        return jsonify({"status": "ok"}), 200

    @app.route('/switch_status/<status>/', methods=['POST'])
    def switch_status(status: str):
        if 'usuario_id' not in session:
            return render_template("login.html")
        
        usuario_id = session['usuario_id']

        estado_existente = EstadoUsuario.query.filter_by(usuario_id=usuario_id).first()

        if not estado_existente:
            nuevo_estado = EstadoUsuario(usuario_id=usuario_id, estado=status)
            db.session.add(nuevo_estado)
            db.session.commit()
            return jsonify({
                'status': status
            }), 200
            
        estado_existente.estado = status
        db.session.commit()
        return jsonify({
            'status': status
        }), 200
    
    @app.route('/received_requests', methods=['GET'])
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
    
    @app.route('/request_response', methods=['POST'])
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

    @app.route('/link_request', methods=['GET', 'POST']) # envía solicitud de vinculación escribiendo datos en tabla solicitud_vinculacion
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
        
        revisar_nuevas_notificaciones(usuario_id)
        
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
        
        revisar_nuevas_notificaciones(usuario_id)
        
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
        role_obj = Rol.query.all()
        roles = [{'id': role.id, 'rol': role.rol} for role in role_obj]
        # print(roles)

        if request.method == 'POST':
            nombre = request.form["nombre"]
            email = request.form["email"]
            contrasena = request.form["contrasena"]
            repetir_contrasena = request.form["repetir_contrasena"]
            rol = request.form["role"]
            
            if contrasena != repetir_contrasena:
                return "Las contraseñas no coinciden, intenta nuevamente."
            
            if Usuario.query.filter_by(correo=email).first():
                return "El correo ya está registrado, intenta con otro."
            
            contrasena_hash = generate_password_hash(contrasena)
            
            nuevo_usuario = Usuario(nombre=nombre, correo=email, contrasena=contrasena_hash, rol=rol)
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            return redirect(url_for("login"))
        return render_template("registro.html", roles=roles, rol_seleccionado='student')
        
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
                
                usuario_id = session.get('usuario_id')
                supervisor = Usuario.query.join(Rol).filter(Usuario.id == usuario_id, Rol.nombre == "supervisor").first()
                
                if supervisor:
                    session["supervisor_id"] = usuario_id

                session.permanent = True

                nueva_notificacion = NuevaNotificacion.query.filter_by(usuario_id=usuario_id).first()

                if not nueva_notificacion:
                    entrada_default = NuevaNotificacion(usuario_id=usuario_id, estado=False)
                    db.session.add(entrada_default)
                    db.session.commit()

                return redirect(url_for("home"))
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
        
        revisar_nuevas_notificaciones(usuario_id)
        
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

        revisar_nuevas_notificaciones(usuario_id)

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
        session.pop("supervisor_id", None)
        return redirect(url_for("home"))

    @app.route("/")
    def home():
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        
        usuario_id = session.get('usuario_id')
        supervisor = Usuario.query.join(Rol).filter(Usuario.id == usuario_id, Rol.nombre == "supervisor").first()

        if supervisor:
            session["supervisor_id"] = usuario_id

            Estudiante = aliased(Usuario)
            Supervisor = aliased(Usuario)

            query = (
                db.session.query(
                    Estudiante.id,
                    Estudiante.nombre,
                    Tiempo.tiempo,
                    EstadoUsuario.estado
                )
                .select_from(SupervisorEstudiante)
                .join(Supervisor, Supervisor.id == SupervisorEstudiante.supervisor_id)
                .join(Estudiante, Estudiante.id == SupervisorEstudiante.estudiante_id)
                .outerjoin(Tiempo, Tiempo.usuario_id == SupervisorEstudiante.estudiante_id)
                .outerjoin(EstadoUsuario, EstadoUsuario.usuario_id == SupervisorEstudiante.estudiante_id)
                .filter(SupervisorEstudiante.supervisor_id == usuario_id)
                .distinct(Estudiante.id)
            )

            estudiantes = [
                {"id": eid, "nombre": nombre, "tiempo": tiempo, "estado": estado}
                for eid, nombre, tiempo, estado in query.all()
            ]
            printn(estudiantes)
            return render_template("s_dashboard.html", estudiantes=estudiantes)
        
        return redirect(url_for("perfil"))
    
    @app.route('/notifications')
    @login_required
    def notifications():
        usuario_id = session.get('usuario_id')
        NuevaNotificacion.query.filter_by(usuario_id=usuario_id).update({ 'estado': False })
        db.session.commit()
        
        query = (
            Notificaciones.query
            .filter_by(usuario_id=usuario_id)
            .order_by(desc(Notificaciones.fecha))
            .all()
        )

        return render_template("notificaciones.html", notificaciones=query)
    
    @app.route('/grade_record/<id>', methods=['GET', 'POST'])
    @supervisor_required
    def grade_record(id):
        if request.method == 'POST':
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
            
            repo = NotificationRepository(db.session)
            notification = Notification(id, repo)
            asignatura_nombre = Asignatura.query.get(asignatura).nombre
            notification.notify_grade(nota, asignatura_nombre, 'add')

            return redirect(url_for("grade_record", id=id))
        
        asignaturas = listar_asignaturas(id)
        registro_notas = listar_registro_notas(id)

        return render_template('s_grade_record.html', asignaturas=asignaturas, registro_notas=registro_notas)

    @app.route("/mark_paid", methods=["POST"])
    @supervisor_required
    def mark_paid():
        data = request.get_json()
        registro_id = data.get('grade_to_pay')
        usuario_id = data.get('usuario_id')
        
        registro = RegistroNotas.query.get_or_404(registro_id)
        registro.estado = True
        nota = registro.nota
        asignatura = registro.asignatura.nombre
        
        repo = NotificationRepository(db.session)
        notification = Notification(usuario_id, repo)
        notification.notify_grade(nota, asignatura, 'pay')
        
        return redirect(url_for("grade_record", id=usuario_id))
