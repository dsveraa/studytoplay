import pytest
from app.models.notificaciones_model import NuevaNotificacion

@pytest.fixture
def sample_notifications(usuario):
    from app import db
    from app.models.notificaciones_model import Notificaciones, NuevaNotificacion
    from datetime import datetime

    n1 = Notificaciones(usuario_id=usuario.id, notificacion="Mensaje 1", fecha=datetime.now())
    n2 = Notificaciones(usuario_id=usuario.id, notificacion="Mensaje 2", fecha=datetime.now())
    nueva = NuevaNotificacion(usuario_id=usuario.id, estado=True)
    
    db.session.add_all([n1, n2, nueva])
    db.session.commit()
    
    return [n1, n2], nueva

def test_notifications_route_marks_new_as_false(client, sample_notifications, usuario, db_session):
    notifications, nueva_notificacion = sample_notifications

    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    response = client.get("/notifications")
    assert response.status_code == 200

    html = response.data.decode("utf-8")

    for n in notifications:
        assert n.notificacion in html

    updated = db_session.query(NuevaNotificacion).filter_by(usuario_id=usuario.id).first()
    assert updated.estado is False


def test_notifications_requires_login(client):
    with client.session_transaction() as sess:
        sess.pop("usuario_id", None)

    response = client.get("/notifications")
    assert response.status_code in (302, 401)
