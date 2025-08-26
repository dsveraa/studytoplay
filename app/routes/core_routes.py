from flask import render_template, request, redirect, url_for, session, jsonify, Blueprint
from sqlalchemy import func
from sqlalchemy.orm import aliased

from app.models import Estudio, Tiempo, Usuario, Asignatura, Rol, SupervisorEstudiante, EstadoUsuario, Incentivos, Restricciones
from app.utils.helpers import asignar_estrellas, asignar_nivel, asignar_trofeos, crear_plantilla_estrellas, mostrar_estrellas, mostrar_trofeos, mostrar_nivel, relation_required, supervisor_required, revisar_nuevas_notificaciones
from app.services.settings_service import UserSettings
from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive

from .. import db

from typing import List
from app.utils.debugging_utils import printn

from user_agents import parse
import logging


core_bp = Blueprint('core', __name__)

@core_bp.route("/")
def home():
    from app.models import Settings

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))
    
    usuario_id = session.get('usuario_id')
    supervisor = Usuario.query.join(Rol).filter(Usuario.id == usuario_id, Rol.nombre == "supervisor").first()

    settings = UserSettings(usuario_id)
    settings.information()
    
    if supervisor:
        session["supervisor_id"] = usuario_id

        Estudiante = aliased(Usuario)
        Supervisor = aliased(Usuario)

        query = (
            db.session.query(
                Estudiante.id,
                Estudiante.nombre,
                Tiempo.tiempo,
                EstadoUsuario.estado,
                Settings.incentivo_notas
            )
            .select_from(SupervisorEstudiante)
            .join(Supervisor, Supervisor.id == SupervisorEstudiante.supervisor_id)
            .join(Estudiante, Estudiante.id == SupervisorEstudiante.estudiante_id)
            .outerjoin(Tiempo, Tiempo.usuario_id == SupervisorEstudiante.estudiante_id)
            .outerjoin(EstadoUsuario, EstadoUsuario.usuario_id == SupervisorEstudiante.estudiante_id)
            .outerjoin(Settings, Settings.usuario_id == Estudiante.id)
            .filter(SupervisorEstudiante.supervisor_id == usuario_id)
            .distinct(Estudiante.id)
        )

        estudiantes = [
            {"id": eid, 
                "nombre": nombre, 
                "tiempo": tiempo, 
                "estado": estado, 
                "grade_incentive": incentivo_notas
                }
            for eid, nombre, tiempo, estado, incentivo_notas in query.all()
        ]
        printn(estudiantes)
        return render_template("s_dashboard.html", estudiantes=estudiantes)
    
    return redirect(url_for("core.perfil"))

@core_bp.route("/settings/<id>")
@supervisor_required
@relation_required
def settings(id=None):
    from app.services.countries_service import get_countries
    from app.utils.sistemas_notas_utils import sistemas
    
    repo = GradeIncentiveRepository(db.session)
    management = GradeIncentive(id, repo)

    incentivos, restricciones = management.list_information()

    settings = UserSettings(id)
    incentivo_notas = settings.consultar_incentivo_notas()

    lista_paises = get_countries()
    pais_actual = settings.consultar_pais()

    return render_template("s_settings.html", 
                            incentivo_notas=incentivo_notas, 
                            estudiante_id=id, 
                            paises=lista_paises,
                            pais_actual=pais_actual,
                            incentivos=incentivos,
                            restricciones=restricciones,
                            sistemas=sistemas
                            )

@core_bp.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))
    
    usuario_id = session["usuario_id"]
    usuario_nombre = session["usuario_nombre"]

    resultados = (
        db.session.query(
            Estudio.asignatura_id,
            func.sum(
                func.extract('epoch', Estudio.fecha_fin - Estudio.fecha_inicio)
            ).label("total_segundos")
        )
        .filter(Estudio.usuario_id == usuario_id)
        .group_by(Estudio.asignatura_id)
        .all()
    )

    tiempos = {asig_id: tiempo for asig_id, tiempo in resultados}

    asignaturas = {a.id: a.nombre for a in Asignatura.query.filter_by(usuario_id=usuario_id)}

    total = sum(tiempos.values())

    porcentajes_asignaturas = {
        nombre: str(round((tiempos.get(asig_id, 0) / total * 100), 1)) if total > 0 else "0.0"
        for asig_id, nombre in asignaturas.items()
    }

    nivel: int = mostrar_nivel(usuario_id)
    trofeos: int = mostrar_trofeos(usuario_id)
    cantidad_estrellas: int = mostrar_estrellas(usuario_id)
    estrellas: List[int] = crear_plantilla_estrellas(cantidad_estrellas)
    revisar_nuevas_notificaciones(usuario_id)
    asignar_nivel(usuario_id)
    asignar_estrellas(usuario_id)
    asignar_trofeos(usuario_id)

    incentivos_obj = Incentivos.query.filter_by(usuario_id=usuario_id).all()
    restricciones_obj = Restricciones.query.filter_by(usuario_id=usuario_id).all()

    incentivos = [incentivo.condicion for incentivo in incentivos_obj]
    restricciones = [restriccion.restriccion for restriccion in restricciones_obj]

    return render_template(
        "perfil.html", 
        id=usuario_id, 
        nombre=usuario_nombre, 
        estudios=resultados, 
        porcentajes_asignaturas=porcentajes_asignaturas,
        nivel=nivel,
        estrellas=estrellas,
        trofeos=trofeos,
        incentivos=incentivos,
        restricciones=restricciones
        )

@core_bp.route("/change_country", methods=["POST"])
def change_country():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    pais_id = data.get('pais_id')

    if not estudiante_id:
        return jsonify({"error": "estudiante_id missing"}), 400
    
    if not pais_id:
        return jsonify({"error": "pais_id missing"}), 400
    
    settings = UserSettings(estudiante_id)
    result = settings.cambiar_pais(pais_id)

    return jsonify({"success": True, "result": result})

@core_bp.route("/incentivo_toggle", methods=["POST"])
def incentivo_toggle():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')

    if not estudiante_id:
        return jsonify({"error": "estudiante_id missing"}), 400

    settings = UserSettings(estudiante_id)
    result = settings.incentivo_toggle()        

    return jsonify({"success": True, "result": result})

@core_bp.route('/log_click', methods=['POST'])
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
