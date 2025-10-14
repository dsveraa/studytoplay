import pytest
from unittest.mock import MagicMock, patch


with patch("app.routes.gamification_routes.relation_required") as fake_decorator:
    fake_decorator.side_effect = lambda f: f
    from app.routes.gamification_routes import gamificacion_bp


@pytest.fixture
def incentive_data(supervisor_and_student):
    _, estudiante = supervisor_and_student
    return {
        "estudiante_id": estudiante.id,
        "monto": "1000",
        "nota": "7.0",
        "simbolo": "$",
        "moneda": "USD"
    }


@patch("app.routes.gamification_routes.relation_required")
def test_add_incentive_missing_fields(mock_relation_required, client, supervisor_and_student):
    mock_relation_required.return_value = lambda f: f
    supervisor, estudiante = supervisor_and_student

    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    data = {
        "estudiante_id": estudiante.id,
        "monto": "1000",
        "nota": "7.0",
        "simbolo": "$"
    }

    response = client.post("/incentive", json=data)

    assert response.status_code == 400
    assert "moneda missing" in response.get_json()["error"]


@patch("app.routes.gamification_routes.GamificacionService")
@patch("app.routes.gamification_routes.GradeIncentiveRepository")
@patch("app.routes.gamification_routes.GradeIncentive")
def test_add_incentive_success(mock_incentive_class, mock_repo_class, mock_service, client, supervisor_and_student, incentive_data):
    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo

    mock_incentive = MagicMock()
    mock_incentive_class.return_value = mock_incentive

    mock_last = MagicMock()
    mock_last.id = 1
    mock_last.condicion = "Bonificación por nota 7.0"
    mock_service.get_last_incentive.return_value = mock_last

    supervisor, _ = supervisor_and_student
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    response = client.post("/incentive", json=incentive_data)
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["id"] == 1
    assert json_data["incentivo"] == "Bonificación por nota 7.0"
    assert json_data["estudiante_id"] == incentive_data["estudiante_id"]

    mock_repo_class.assert_called_once()
    mock_incentive_class.assert_called_once_with(incentive_data["estudiante_id"], mock_repo)
    mock_incentive.add_incentive.assert_called_once_with(
        incentive_data["monto"],
        incentive_data["nota"],
        incentive_data["simbolo"],
        incentive_data["moneda"]
    )
    mock_service.get_last_incentive.assert_called_once_with(incentive_data["estudiante_id"])


@patch("app.routes.gamification_routes.relation_required")
@patch("app.routes.gamification_routes.GradeIncentiveRepository")
@patch("app.routes.gamification_routes.GradeIncentive")
def test_delete_incentive_success(mock_incentive_class, mock_repo_class, mock_relation_required, client, supervisor_and_student):
    mock_relation_required.return_value = lambda f: f

    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo

    mock_incentive = MagicMock()
    mock_incentive_class.return_value = mock_incentive

    supervisor, estudiante = supervisor_and_student
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    incentive_id = "1"  # Cambiar a cadena
    response = client.delete(f"/incentive/{estudiante.id}/{incentive_id}")

    assert response.status_code == 204

    mock_repo_class.assert_called_once()
    mock_incentive_class.assert_called_once_with(estudiante.id, mock_repo)
    mock_incentive.remove_incentive.assert_called_once_with(incentive_id)


@patch("app.routes.gamification_routes.relation_required")
@patch("app.routes.gamification_routes.GradeIncentiveRepository")
@patch("app.routes.gamification_routes.GradeIncentive")
def test_delete_incentive_not_found(mock_incentive_class, mock_repo_class, mock_relation_required, client, supervisor_and_student):
    mock_relation_required.return_value = lambda f: f

    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo

    mock_incentive = MagicMock()
    mock_incentive_class.return_value = mock_incentive

    mock_incentive.remove_incentive.side_effect = ValueError("Incentive not found")

    supervisor, estudiante = supervisor_and_student
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    incentive_id = "999" 
    response = client.delete(f"/incentive/{estudiante.id}/{incentive_id}")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Incentive not found"

    mock_repo_class.assert_called_once()
    mock_incentive_class.assert_called_once_with(estudiante.id, mock_repo)
    mock_incentive.remove_incentive.assert_called_once_with(incentive_id)
