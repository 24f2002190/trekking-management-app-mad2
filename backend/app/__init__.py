from flask import Flask
from app.models import db
from app.config import Config
from flask_security import Security, SQLAlchemyUserDatastore

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    return app, user_datastore