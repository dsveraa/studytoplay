from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from decouple import Config, RepositoryEnv
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix
from app.utils.filters_utils import register_filters
import os
import logging

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    env = os.environ.get("ENVIRONMENT", "development")
    env_file = f".env.{env}"
    config_env = Config(RepositoryEnv(env_file))

    app.config['SECRET_KEY'] = config_env('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = config_env('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_env('SQLALCHEMY_TRACK_MODIFICATIONS', cast=bool)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True, 'pool_recycle': 250}

    print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    if env == "production":
        print("Modo producción activo. Los tests no deben ejecutarse aquí.")

    db.init_app(app)
    Migrate(app, db)

    register_filters(app)

    from . import models
    from .routes import register_routes

    register_routes(app)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("app.log"),      # Log a archivo
            logging.StreamHandler()              # Log a consola
        ]
    )
    
    return app
