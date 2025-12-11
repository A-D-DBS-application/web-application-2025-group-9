from flask import Flask
from flask_migrate import Migrate
from .models import db
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        db.create_all()  # Create sql tables for our data models

    from .routes import main
    app.register_blueprint(main)

    return app