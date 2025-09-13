import pytest
from sqlalchemy import text
from app import create_app, db

@pytest.fixture
def app():
    import os
    os.environ['ENVIRONMENT'] = 'testing'
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        # opcional
        db.session.execute(text("TRUNCATE TABLE usuarios CASCADE"))
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
