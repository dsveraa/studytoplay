from flask import render_template, request, redirect, url_for, session, jsonify, Blueprint

from app.services.core_service import CoreService
from app.services.gamification_service import GamificacionService
from app.services.home_service import HomeService
from app.services.record_service import RecordService
from app.services.subject_service import SubjectService
from app.services.user_service import UserService
from app.utils.helpers import id_from_kwargs, show_trophies, show_level, relation_required, supervisor_required
from app.services.settings_service import UserSettings
from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive

from .. import db

from app.utils.debugging_utils import printn

from user_agents import parse
import logging


core_bp = Blueprint('core', __name__)

@core_bp.route("/")
def home():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    user_id = session.get('usuario_id')
    supervisor = UserService.check_role(user_id, 'supervisor')

    UserSettings(user_id) # init
    
    if supervisor:
        students = HomeService.get_students(user_id)
        return render_template("s_dashboard.html", estudiantes=students)
    return redirect(url_for("core.perfil"))

@core_bp.route("/settings/<id>")
@supervisor_required
@relation_required(id_from_kwargs)
def settings(id):
    from app.services.countries_service import get_countries
    from app.utils.grades_system_utils import sistemas
    
    repo = GradeIncentiveRepository(db.session)
    management = GradeIncentive(id, repo)

    incentivos, restricciones = management.list_information()

    settings = UserSettings(id)
    name = settings.name
    incentivo_notas = settings.consultar_incentivo_notas()
    pais_actual = settings.consultar_pais()
    trofeo = settings.get_trophy()
    extra_time = settings.get_extra_time()
    study_fun_ratio = settings.get_study_fun_ratio()
    lista_paises = get_countries()

    return render_template("s_settings.html", 
                            incentivo_notas=incentivo_notas, 
                            estudiante_id=id, 
                            paises=lista_paises,
                            pais_actual=pais_actual,
                            incentivos=incentivos,
                            restricciones=restricciones,
                            sistemas=sistemas,
                            trofeo=trofeo,
                            extra_time=extra_time,
                            study_fun_ratio=study_fun_ratio,
                            name=name
                            )

@core_bp.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
    user_id = session["usuario_id"]
    username = session["usuario_nombre"]
    time_by_subject = RecordService.get_time_by_subject(user_id)
    subject_percent = SubjectService.get_subject_percentage(time_by_subject, user_id)
    level: int = show_level(user_id)
    trophies: int = show_trophies(user_id)
    stars = GamificacionService.get_stars(user_id)
    
    CoreService.check_and_set_up(user_id) # init
    
    incentives_list = GamificacionService.get_incentives(user_id)
    restrictions_list = GamificacionService.get_restrictions(user_id)

    return render_template(
        "perfil.html", 
        id=user_id, 
        nombre=username, 
        estudios=time_by_subject, 
        porcentajes_asignaturas=subject_percent,
        nivel=level,
        estrellas=stars,
        trofeos=trophies,
        incentivos=incentives_list,
        restricciones=restrictions_list
        )

@core_bp.route("/country/<int:estudiante_id>/<int:pais_id>", methods=["PUT"])
@relation_required(id_from_kwargs)
def change_country(estudiante_id, pais_id):
    settings = UserSettings(estudiante_id)
    result = settings.cambiar_pais(pais_id)

    return jsonify({"success": True, "pais_id": result}), 200

@core_bp.route("/incentivo/<int:estudiante_id>", methods=["PUT"])
@relation_required(id_from_kwargs)
def incentivo_toggle(estudiante_id):
    settings = UserSettings(estudiante_id)
    result = settings.incentivo_toggle()

    return jsonify({"success": True, "incentivo": result}), 200

@core_bp.route('/log_click', methods=['POST'])
def log_click():
    data = request.json
    boton = data.get('boton', 'desconocido')
    origen = request.referrer or 'origen desconocido'
    
    ua_strig = request.headers.get('User-Agent', '')
    user_agent = parse(ua_strig)

    navegador = user_agent.browser.family or 'navegador desconocido'
    sistema = user_agent.os.family or 'SO desconocido'

    logging.info(f'Click en: "{boton}", desde "{origen}", usando "{navegador}", en "{sistema}"' )
    return jsonify({"status": "ok"}), 200
