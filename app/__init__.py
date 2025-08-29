from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config.config import config
import os

db = SQLAlchemy()

def create_app(config_name='default'):
    # Get the parent directory (root of the project)
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.api import api_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    
    return app