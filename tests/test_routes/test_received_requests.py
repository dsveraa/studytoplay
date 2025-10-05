from unittest.mock import patch


@patch("app.routes.relaciones_routes.db.session.query")
def test_received_requests_success(mock_query, client, supervisor_and_student):
    supervisor, estudiante = supervisor_and_student

    mock_query.return_value.select_from.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [
        (
            supervisor.id,
            supervisor.nombre,
            estudiante.id,
            estudiante.nombre,
            "pendiente",
            "2025-10-05T12:00:00"
        )
    ]

    with client.session_transaction() as sess:
        sess["usuario_id"] = estudiante.id

    response = client.get("/received_requests")
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["status"] == "ok"
    assert len(json_data["current_requests"]) == 1

    solicitud = json_data["current_requests"][0]
    assert solicitud["supervisor_id"] == supervisor.id
    assert solicitud["supervisor"] == supervisor.nombre
    assert solicitud["estudiante_id"] == estudiante.id
    assert solicitud["estudiante"] == estudiante.nombre
    assert solicitud["estado"] == "pendiente"
    assert solicitud["fecha_solicitud"] == "2025-10-05T12:00:00"


@patch("app.routes.relaciones_routes.db.session.query")
def test_received_requests_no_requests(mock_query, client, supervisor_and_student):
    _, estudiante = supervisor_and_student

    mock_query.return_value.select_from.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = []

    with client.session_transaction() as sess:
        sess["usuario_id"] = estudiante.id

    response = client.get("/received_requests")
    json_data = response.get_json()

    assert response.status_code == 400
    assert json_data["status"] == "error"
    assert json_data["error"] == "query not found"


def test_received_requests_requires_login(client):
    response = client.get("/received_requests")
    json_data = response.get_json()

    assert response.status_code == 401
    assert json_data["status"] == "unauthorized"
    assert json_data["reason"] == "login required"