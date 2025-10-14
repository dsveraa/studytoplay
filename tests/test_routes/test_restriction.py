from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def restriction_data(supervisor_and_student):
    _, estudiante = supervisor_and_student
    return {
        "estudiante_id": estudiante.id,
        "mensaje": "No se permite usar el celular durante el estudio"
    }


@patch("app.routes.gamification_routes.relation_required")
def test_add_restriction_missing_fields(mock_relation_required, client, supervisor_and_student):
    mock_relation_required.return_value = lambda f: f
    supervisor, estudiante = supervisor_and_student

    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    data = {
        "estudiante_id": estudiante.id
    }

    response = client.post("/restriction", json=data)

    assert response.status_code == 400
    assert "mensaje missing" in response.get_json()["error"]


@patch("app.models.gamification_model.Restricciones.query")
@patch("app.routes.gamification_routes.GamificacionService")
@patch("app.routes.gamification_routes.GradeIncentiveRepository")
@patch("app.routes.gamification_routes.GradeIncentive")
def test_add_restriction_success(mock_incentive_class, mock_repo_class, mock_service, mock_restriction_query, client, supervisor_and_student, restriction_data):
    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo

    mock_incentive = MagicMock()
    mock_incentive_class.return_value = mock_incentive

    mock_last_restriction = MagicMock()
    mock_last_restriction.id = 1
    mock_last_restriction.restriccion = restriction_data["mensaje"]
    mock_restriction_query.filter_by.return_value.order_by.return_value.first.return_value = mock_last_restriction

    supervisor, _ = supervisor_and_student
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    response = client.post("/restriction", json=restriction_data)
    json_data = response.get_json()

    assert response.status_code == 201
    assert json_data["restriccion"] == restriction_data["mensaje"]
    assert json_data["estudiante_id"] == restriction_data["estudiante_id"]

    mock_repo_class.assert_called_once()
    mock_incentive_class.assert_called_once_with(restriction_data["estudiante_id"], mock_repo)
    mock_incentive.add_restriction.assert_called_once_with(restriction_data["mensaje"])


@patch("app.routes.gamification_routes.relation_required")
@patch("app.routes.gamification_routes.GradeIncentiveRepository")
@patch("app.routes.gamification_routes.GradeIncentive")
def test_delete_restriction_success(mock_incentive_class, mock_repo_class, mock_relation_required, client, supervisor_and_student):
    mock_relation_required.return_value = lambda f: f

    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo

    mock_incentive = MagicMock()
    mock_incentive_class.return_value = mock_incentive

    supervisor, estudiante = supervisor_and_student
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    restriction_id = 1
    response = client.delete(f"/restriction/{estudiante.id}/{restriction_id}")

    assert response.status_code == 204

    mock_repo_class.assert_called_once()
    mock_incentive_class.assert_called_once_with(estudiante.id, mock_repo)
    mock_incentive.remove_restriction.assert_called_once_with(restriction_id)


@patch("app.routes.gamification_routes.relation_required")
@patch("app.routes.gamification_routes.GradeIncentiveRepository")
@patch("app.routes.gamification_routes.GradeIncentive")
def test_delete_restriction_not_found(mock_incentive_class, mock_repo_class, mock_relation_required, client, supervisor_and_student):
    mock_relation_required.return_value = lambda f: f

    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo

    mock_incentive = MagicMock()
    mock_incentive_class.return_value = mock_incentive

    mock_incentive.remove_restriction.side_effect = ValueError("Restriction not found")

    supervisor, estudiante = supervisor_and_student
    with client.session_transaction() as sess:
        sess["usuario_id"] = supervisor.id

    restriction_id = 999  # ID inexistente
    response = client.delete(f"/restriction/{estudiante.id}/{restriction_id}")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Restriction not found"

    mock_repo_class.assert_called_once()
    mock_incentive_class.assert_called_once_with(estudiante.id, mock_repo)
    mock_incentive.remove_restriction.assert_called_once_with(restriction_id)