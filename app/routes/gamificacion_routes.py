from flask import request, jsonify, Blueprint

from app.services.grade_incentive_service import GradeIncentiveRepository, GradeIncentive

from .. import db


gamificacion_bp = Blueprint('gamificacion', __name__)

@gamificacion_bp.route("/add_incentive", methods=["POST"])
def add_incentive():
    from app.models import Incentivos

    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    monto = data.get('monto')
    nota = data.get('nota')
    simbolo = data.get('simbolo')
    moneda = data.get('moneda')

    if not estudiante_id:
        return jsonify({"error": "estudiante_id missing"}), 400
    
    if not monto:
        return jsonify({"error": "monto missing"}), 400
    
    if not nota:
        return jsonify({"error": "nota missing"}), 400
    
    if not simbolo:
        return jsonify({"error": "simbolo missing"}), 400
    
    if not moneda:
        return jsonify({"error": "moneda missing"}), 400
    
    repo = GradeIncentiveRepository(db.session)
    grade_incentive = GradeIncentive(estudiante_id, repo)
    grade_incentive.add_incentive(monto, nota, simbolo, moneda)

    ultimo = Incentivos.query.filter_by(usuario_id=estudiante_id).order_by(Incentivos.id.desc()).first()

    return jsonify({"id": ultimo.id, "incentivo": ultimo.condicion }), 200
        
@gamificacion_bp.route("/add_restriction", methods=["POST"])
def add_restriction():
    from app.models import Restricciones

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
