from flask import request, jsonify, Blueprint

from app.services.gamification_service import GamificacionService
from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive
from app.models import Restricciones
from app.utils.helpers import id_from_json, id_from_kwargs, relation_required

from .. import db


gamificacion_bp = Blueprint('gamificacion', __name__)

@gamificacion_bp.route("/incentive", methods=["POST"])
@relation_required(id_from_json)
def add_incentive():
    data = request.get_json()
    student_id = data.get('estudiante_id')
    amount = data.get('monto')
    grade = data.get('nota')
    symbol = data.get('simbolo')
    currency = data.get('moneda')

    required_fields = ['estudiante_id', 'monto', 'nota', 'simbolo', 'moneda']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} missing"}), 400
    
    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(student_id, repo)
    grade_incentive.add_incentive(amount, grade, symbol, currency)

    last_one = GamificacionService.get_last_incentive(student_id)

    return jsonify({"id": last_one.id, "incentivo": last_one.condicion, "estudiante_id": student_id }), 200
        
@gamificacion_bp.route("/restriction", methods=["POST"])
@relation_required(id_from_json)
def add_restriction():
    data = request.get_json()
    student_id = data.get('estudiante_id')
    message = data.get('mensaje')

    if not student_id:
        return jsonify({"error": "estudiante_id missing"}), 400
    
    if not message:
        return jsonify({"error": "mensaje missing"}), 400

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(student_id, repo)
    grade_incentive.add_restriction(message)

    last_one = Restricciones.query.filter_by(usuario_id=student_id).order_by(Restricciones.id.desc()).first()

    return jsonify({"id": last_one.id, "restriccion": last_one.restriccion, "estudiante_id": student_id}), 201

@gamificacion_bp.route("/incentive/<int:estudiante_id>/<incentive_id>", methods=["DELETE"])
@relation_required(id_from_kwargs)
def delete_incentive(estudiante_id, incentive_id):
    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    try:
        grade_incentive.remove_incentive(incentive_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"success": "ok"}), 204

@gamificacion_bp.route("/restriction/<int:estudiante_id>/<int:restriction_id>", methods=["DELETE"])
@relation_required(id_from_kwargs)
def delete_restriction(estudiante_id, restriction_id):
    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    try:
        grade_incentive.remove_restriction(restriction_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"success": "ok"}), 204
