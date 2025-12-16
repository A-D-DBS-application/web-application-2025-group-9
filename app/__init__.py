from flask import Flask
from flask_migrate import Migrate
from .models import db
from .config import Config
import re

def format_bucket(value):
    """Format bucket strings to readable format"""
    if not value or not isinstance(value, str):
        return value
    
    # Remove 'Bucket' prefix if present
    formatted = value.replace('Bucket', '')
    
    # Handle 'Above' pattern (e.g., Above500M -> >€500M or >500M)
    if 'Above' in formatted:
        formatted = formatted.replace('Above', '>')
        # Add € for revenue buckets (containing M or K)
        if 'M' in formatted or 'K' in formatted:
            formatted = formatted.replace('>', '>€')
    
    # Handle 'Below' pattern (e.g., Below50K -> <€50K)
    elif 'Below' in formatted:
        formatted = formatted.replace('Below', '<')
        if 'M' in formatted or 'K' in formatted:
            formatted = formatted.replace('<', '<€')
    
    # Handle range pattern with underscores (e.g., 2000_4999 -> 2000-4999)
    elif '_' in formatted:
        formatted = formatted.replace('_', '-')
        # If it's a number range without M/K, assume it's employees
        if not ('M' in formatted or 'K' in formatted):
            formatted += ' werknemers'
    
    return formatted

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()  # Create sql tables for our data models

    from .routes import main
    app.register_blueprint(main)
    
    # Register custom Jinja2 filter
    app.jinja_env.filters['bucket'] = format_bucket

    return app