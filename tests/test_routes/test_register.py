import pytest
from flask import session
from werkzeug.security import generate_password_hash
from app import db
from app.models import Usuario, Rol, NuevaNotificacion
from app.services.user_service import UserService


@pytest.fixture
def roles(app):
    rol_student = Rol(nombre="student")
    rol_supervisor = Rol(nombre="supervisor")
    db.session.add_all([rol_student, rol_supervisor])
    db.session.commit()
    return rol_student, rol_supervisor


def test_registro_view_default_role(client, roles):
    student, _ = roles
    resp = client.get("/registro")
    assert resp.status_code == 200
    # Debe tener rol_default.id
    assert str(student.id).encode() in resp.data


def test_registro_view_with_querystring(client, roles):
    _, supervisor = roles
    resp = client.get(f"/registro?rol_seleccionado={supervisor.id}")
    assert resp.status_code == 200
    assert str(supervisor.id).encode() in resp.data


def test_registro_email_already_used(client, roles):
    student, _ = roles
    usuario = Usuario(
        nombre="Existente",
        correo="existente@example.com",
        contrasena=generate_password_hash("abc123"),
        rol=student,
    )
    db.session.add(usuario)
    db.session.commit()

    resp = client.post(
        "/registro",
        data={
            "nombre": "Nuevo",
            "email": "existente@example.com",
            "contrasena": "abc123",
            "repetir_contrasena": "abc123",
            "role": str(student.id),
        },
    )
    assert resp.status_code == 200
    assert b"E-mail <b>existente@example.com</b> is already used." in resp.data


def test_registro_password_mismatch(client, roles):
    student, _ = roles
    resp = client.post(
        "/registro",
        data={
            "nombre": "Nuevo",
            "email": "nuevo@example.com",
            "contrasena": "abc123",
            "repetir_contrasena": "otra",
            "role": str(student.id),
        },
    )
    assert resp.status_code == 200
    assert b"Passwords doesn't match, try again." in resp.data


def test_registro_both_errors(client, roles):
    student, _ = roles
    usuario = Usuario(
        nombre="Existente",
        correo="existente@example.com",
        contrasena=generate_password_hash("abc123"),
        rol=student,
    )
    db.session.add(usuario)
    db.session.commit()

    resp = client.post(
        "/registro",
        data={
            "nombre": "Nuevo",
            "email": "existente@example.com",
            "contrasena": "abc123",
            "repetir_contrasena": "otra",
            "role": str(student.id),
        },
    )
    assert resp.status_code == 200
    assert b"E-mail <b>existente@example.com</b> is already used." in resp.data
    assert b"Passwords doesn't match, try again." in resp.data


def test_registro_success_student(client, roles):
    student, _ = roles
    resp = client.post(
        "/registro",
        data={
            "nombre": "Nuevo",
            "email": "nuevo@example.com",
            "contrasena": "abc123",
            "repetir_contrasena": "abc123",
            "role": "1",  # fuerza que entre al branch de student
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/login" in resp.location

    usuario = Usuario.query.filter_by(correo="nuevo@example.com").first()
    assert usuario is not None
    notificacion = NuevaNotificacion.query.filter_by(usuario_id=usuario.id).first()
    assert notificacion is not None


def test_registro_success_supervisor(client, roles):
    _, supervisor = roles
    resp = client.post(
        "/registro",
        data={
            "nombre": "Sup",
            "email": "sup@example.com",
            "contrasena": "abc123",
            "repetir_contrasena": "abc123",
            "role": str(supervisor.id),
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/login" in resp.location

    usuario = Usuario.query.filter_by(correo="sup@example.com").first()
    assert usuario is not None
    assert usuario.rol.nombre == "supervisor"
    notificacion = NuevaNotificacion.query.filter_by(usuario_id=usuario.id).first()
    assert notificacion is not None
