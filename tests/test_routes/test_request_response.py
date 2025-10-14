from unittest.mock import MagicMock, patch


@patch("app.models.SupervisorEstudiante.query")
@patch("app.models.SolicitudVinculacion.query")
@patch("app.routes.relationship_routes.db.session.commit")
@patch("app.routes.relationship_routes.enviar_notificacion_respuesta_lr")
def test_request_response_accept(
    mock_enviar_notificacion, mock_commit, mock_solicitud_query, mock_relacion_query, client, supervisor_and_student_no_relation
):
    supervisor, estudiante = supervisor_and_student_no_relation

    mock_solicitud = MagicMock()
    mock_solicitud.supervisor_id = supervisor.id
    mock_solicitud.estudiante_id = estudiante.id
    mock_solicitud.estado = "pendiente"
    mock_solicitud.supervisor = supervisor

    mock_solicitud_query.filter_by.return_value.order_by.return_value.first.return_value = mock_solicitud

    mock_relacion_query.filter_by.return_value.first.return_value = None

    with client.session_transaction() as sess:
        sess["usuario_id"] = estudiante.id

    response = client.post(
        "/request_response",
        json={"sid": 1, "response": "aceptada"},
    )
    json_data = response.get_json()

    assert response.status_code == 201
    assert json_data["status"] == "success"
    assert json_data["response"] == "aceptada"

    mock_enviar_notificacion.assert_called_once_with(
        supervisor.correo, "aceptada", estudiante.id
    )


@patch("app.routes.relationship_routes.SolicitudVinculacion.query")
def test_request_response_request_not_found(mock_query, client, supervisor_and_student):
    _, estudiante = supervisor_and_student

    mock_query.filter_by.return_value.order_by.return_value.first.return_value = None

    with client.session_transaction() as sess:
        sess["usuario_id"] = estudiante.id

    response = client.post(
        "/request_response",
        json={"sid": 999, "response": "aceptada"},
    )
    json_data = response.get_json()

    assert response.status_code == 404
    assert json_data["status"] == "failed"
    


def test_request_response_invalid_params(client, supervisor_and_student):
    _, estudiante = supervisor_and_student

    with client.session_transaction() as sess:
        sess["usuario_id"] = estudiante.id

    response = client.post(
        "/request_response",
        json={"sid": None, "response": "invalid_response"},
    )
    json_data = response.get_json()

    assert response.status_code == 404
    assert json_data["status"] == "failed"
    assert json_data["error"] == "Invalid params"


def test_request_response_requires_login(client):
    response = client.post(
        "/request_response",
        json={"sid": 1, "response": "aceptada"},
    )
    json_data = response.get_json()

    assert response.status_code == 401
    assert json_data["status"] == "unauthorized"
    assert json_data["reason"] == "login required"