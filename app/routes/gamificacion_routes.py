from flask import request, jsonify, Blueprint

from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive
from app.models import Incentivos, Restricciones

from .. import db


gamificacion_bp = Blueprint('gamificacion', __name__)

@gamificacion_bp.route("/add_incentive", methods=["POST"])
def add_incentive():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    monto = data.get('monto')
    nota = data.get('nota')
    simbolo = data.get('simbolo')
    moneda = data.get('moneda')

    required_fields = ['estudiante_id', 'monto', 'nota', 'simbolo', 'moneda']
    
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} missing"}), 400
    
    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    grade_incentive.add_incentive(monto, nota, simbolo, moneda)

    ultimo = Incentivos.query.filter_by(usuario_id=estudiante_id).order_by(Incentivos.id.desc()).first()

    return jsonify({"id": ultimo.id, "incentivo": ultimo.condicion }), 200
        
@gamificacion_bp.route("/add_restriction", methods=["POST"])
def add_restriction():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    mensaje = data.get('mensaje')

    if not estudiante_id:
        return jsonify({"error": "estudiante_id missing"}), 400
    
    if not mensaje:
        return jsonify({"error": "mensaje missing"}), 400

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    grade_incentive.add_restriction(mensaje)

    ultima = Restricciones.query.filter_by(usuario_id=estudiante_id).order_by(Restricciones.id.desc()).first()

    return jsonify({"id": ultima.id, "restriccion": ultima.restriccion}), 200

@gamificacion_bp.route("/delete_incentive", methods=["POST"])
def delete_incentive():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    incentive_id = data.get('incentive_id')

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    grade_incentive.remove_incentive(incentive_id)
    
    return jsonify({"success": "ok"}), 200

@gamificacion_bp.route("/delete_restriction", methods=["POST"])
def delete_restriction():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    restriction_id = data.get('restriction_id')

    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    grade_incentive.remove_restriction(restriction_id)
    
    return jsonify({"success": "ok"}), 200
