from app.models import EstadoUsuario
from app import db


def test_switch_status_crea_estado(client, app, usuario):
    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    resp = client.post("/switch_status/activo/")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "activo"

    with app.app_context():
        estado = EstadoUsuario.query.filter_by(usuario_id=usuario.id).first()
        assert estado is not None
        assert estado.estado == "activo"


def test_switch_status_actualiza_estado(client, app, usuario):
    with app.app_context():
        estado = EstadoUsuario(usuario_id=usuario.id, estado="inactivo")
        db.session.add(estado)
        db.session.commit()

    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    resp = client.post("/switch_status/activo/")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "activo"

    with app.app_context():
        estado = EstadoUsuario.query.filter_by(usuario_id=usuario.id).first()
        assert estado.estado == "activo"


def test_switch_status_requiere_login(client):
    resp = client.post("/switch_status/activo/")
    assert resp.status_code in (302, 401)
