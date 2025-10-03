import pytest
from flask import session
from app.models import Estudio, Asignatura, Incentivos, Restricciones
from app import db
from datetime import datetime, timedelta

@pytest.fixture
def asignatura(usuario):
    asign = Asignatura(
        nombre="Matemáticas",
        usuario_id=usuario.id
    )
    db.session.add(asign)
    db.session.commit()
    return asign

@pytest.fixture
def estudio(usuario, asignatura):
    estudio = Estudio(
        usuario_id=usuario.id,
        asignatura_id=asignatura.id,
        resumen="Sesión de prueba",
        fecha_inicio=datetime(2025, 10, 1, 10, 0, 0),
        fecha_fin=datetime(2025, 10, 1, 11, 0, 0)
    )
    db.session.add(estudio)
    db.session.commit()
    return estudio

@pytest.fixture
def incentivo(usuario):
    inc = Incentivos(usuario_id=usuario.id, condicion="cualquier incentivo")
    db.session.add(inc)
    db.session.commit()
    return inc

@pytest.fixture
def restriccion(usuario):
    res = Restricciones(usuario_id=usuario.id, restriccion="Ed. Física")
    db.session.add(res)
    db.session.commit()
    return res


def test_perfil_redirect_if_not_logged(client):
    response = client.get("/perfil")
    assert response.status_code == 302
    assert "/login" in response.location


def test_perfil_render_with_data(client, usuario, asignatura, estudio, incentivo, restriccion):
    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id
        sess["usuario_nombre"] = usuario.nombre

    response = client.get("/perfil")

    assert response.status_code == 200
    html = response.data.decode()

    assert "Profile" in html
    assert "Welcome" in html

