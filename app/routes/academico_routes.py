from flask import render_template, request, redirect, url_for, session, jsonify, Blueprint
from sqlalchemy import desc

from app.models import Estudio, Asignatura, EstadoUsuario
from app.utils.helpers import login_required, revisar_nuevas_notificaciones

from .. import db


academico_bp = Blueprint('academico', __name__)

@academico_bp.route('/switch_status/<status>/', methods=['POST'])
@login_required
def switch_status(status: str):
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
    
@academico_bp.route('/edit_record/<id>', methods=["GET", "POST"])
def edit_record(id):
    usuario_id = session.get("usuario_id")
    summary_obj = Estudio.query.filter_by(id=id, usuario_id=usuario_id).first()
    summary = summary_obj.resumen

    if request.method == 'POST':
        data = request.get_json()
        summary = data.get('summary')
        summary_obj.resumen = summary
        db.session.commit()
        return redirect(url_for("core.perfil"))

    return render_template("edit_record.html", summary=summary)



@academico_bp.route("/records")
@academico_bp.route("/records/<activity_id>")
def records(activity_id=None):
    if "usuario_id" not in session:
        return redirect(url_for("auth.login_view"))
    
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
