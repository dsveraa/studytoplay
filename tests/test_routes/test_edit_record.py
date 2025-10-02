import pytest
from app import db
from app.models import Estudio

@pytest.fixture
def estudio_test(usuario):
    estudio = Estudio(
        usuario_id=usuario.id,
        resumen="Resumen de prueba",
        fecha_inicio="2025-10-01",
        fecha_fin="2025-10-02"
    )
    db.session.add(estudio)
    db.session.commit()

    yield estudio

    db.session.delete(estudio)
    db.session.commit()


def test_view_edit_record(client, usuario, estudio_test):
    with client.session_transaction() as sess:
        sess['usuario_id'] = usuario.id

    response = client.get(f'/edit_record/{estudio_test.id}')
    assert response.status_code == 200
    assert b"Resumen de prueba" in response.data


def test_edit_record(client, usuario, estudio_test):
    with client.session_transaction() as sess:
        sess['usuario_id'] = usuario.id

    new_summary = "Resumen actualizado desde test"

    response = client.post(
        f'/edit_record/{estudio_test.id}',
        json={'summary': new_summary}
    )

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/perfil')

    updated_estudio = db.session.get(Estudio, estudio_test.id)
    assert updated_estudio.resumen == new_summary
