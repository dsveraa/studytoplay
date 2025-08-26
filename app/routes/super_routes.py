from flask import render_template, request, redirect, url_for, Blueprint
from sqlalchemy import desc

from app.models import Estudio, Uso, Asignatura, RegistroNotas
from app.utils.helpers import relation_required, supervisor_required, listar_asignaturas, listar_registro_notas
from app.services.notifications_service import Notification, NotificationRepository
from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive, get_currency_data

from .. import db


super_bp = Blueprint('super', __name__)

@super_bp.route('/student_info/<id>', methods=['GET'])
@supervisor_required
@relation_required
def student_info(id):
    
    activity_obj = Estudio.query.filter_by(usuario_id=id).order_by(desc(Estudio.id)).limit(5).all()
    use_obj = Uso.query.filter_by(usuario_id=id).order_by(desc(Uso.id)).limit(10).all()

    return render_template("s_records.html", estudios=activity_obj, usos=use_obj)

@super_bp.route('/grade_record/<id>', methods=['GET', 'POST'])
@supervisor_required
@relation_required
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

        asignatura_nombre = Asignatura.query.get(asignatura).nombre

        amount, currency, symbol = get_currency_data(id, nota)

        repo = NotificationRepository(db.session)
        notification = Notification(id, repo)
        notification.notify_grade(nota, asignatura_nombre, 'add', amount, currency, symbol)

        return redirect(url_for("super.grade_record", id=id))
    
    asignaturas = listar_asignaturas(id)
    registro_notas = listar_registro_notas(id)

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(id, repo)
    best_grades = grade_incentive.filter_grades()

    return render_template('s_grade_record.html', asignaturas=asignaturas, registro_notas=registro_notas, best_grades=best_grades)

@super_bp.route("/mark_paid", methods=["POST"])
@supervisor_required
def mark_paid():
    data = request.get_json()
    registro_id = data.get('grade_to_pay')
    usuario_id = data.get('usuario_id')
    
    registro = RegistroNotas.query.get_or_404(registro_id)
    registro.estado = True
    nota = registro.nota
    asignatura = registro.asignatura.nombre
    
    amount, currency, symbol = get_currency_data(usuario_id, nota)

    repo = NotificationRepository(db.session)
    notification = Notification(usuario_id, repo)
    notification.notify_grade(nota, asignatura, 'pay', amount, currency, symbol)
    
    return redirect(url_for("super.grade_record", id=usuario_id))

