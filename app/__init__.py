from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from decouple import config
from datetime import timedelta
import markdown

from werkzeug.middleware.proxy_fix import ProxyFix
import logging


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.config['SECRET_KEY'] = config('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config('SQLALCHEMY_TRACK_MODIFICATIONS')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    print("DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    Migrate(app, db)

    from . import models
    from .routes import register_routes

    register_routes(app)

    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown.markdown(text or "", extensions=["extra", "fenced_code", "tables"])

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