import pytest
from flask import url_for
from app import db
from app.models import Usuario, Rol, Asignatura, Estudio
from werkzeug.security import generate_password_hash


@pytest.fixture
def usuario_con_asignaturas(app):
    rol = db.session.query(Rol).first()
    if not rol:
        rol = Rol(nombre="TestRole")
        db.session.add(rol)
        db.session.commit()

    usuario = Usuario(
        nombre="Usuario Test",
        correo="test_records@example.com",
        contrasena=generate_password_hash("password123"),
        rol_id=rol.id
    )
    db.session.add(usuario)
    db.session.commit()

    asignatura = Asignatura(nombre="Matemáticas", usuario_id=usuario.id)
    db.session.add(asignatura)
    db.session.commit()

    estudio = Estudio(
        usuario_id=usuario.id,
        asignatura_id=asignatura.id,
        resumen="Primer estudio",
        fecha_inicio="2025-10-01",
        fecha_fin="2025-10-02"
    )
    db.session.add(estudio)
    db.session.commit()

    yield usuario, asignatura, estudio


def test_records_requires_login(client):
    """Debe redirigir al login si no hay usuario en sesión"""
    resp = client.get("/records")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_records_without_activity_id(client, usuario_con_asignaturas):
    """Debe mostrar los últimos estudios si no se pasa activity_id"""
    usuario, asignatura, estudio = usuario_con_asignaturas

    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    resp = client.get("/records")
    assert resp.status_code == 200
    assert b"Primer estudio" in resp.data
    assert b"Latest" in resp.data


def test_records_with_activity_id(client, usuario_con_asignaturas):
    """Debe filtrar por asignatura cuando se pasa activity_id"""
    usuario, asignatura, estudio = usuario_con_asignaturas

    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    resp = client.get(f"/records/{asignatura.id}")
    assert resp.status_code == 200
    assert b"Primer estudio" in resp.data


def test_records_with_unknown_activity_id(client, usuario_con_asignaturas):
    """Si la asignatura no existe, usa 'Unknown' como nombre"""
    usuario, asignatura, estudio = usuario_con_asignaturas

    with client.session_transaction() as sess:
        sess["usuario_id"] = usuario.id

    resp = client.get("/records/9999")
    assert resp.status_code == 200
    assert b"Primer estudio" not in resp.data
    assert b"Unknown" in resp.data
