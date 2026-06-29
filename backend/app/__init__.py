from flask import Flask
from flask_cors import CORS
from app.models import db
from app.config import Config
from flask_security import Security, SQLAlchemyUserDatastore

security = None
user_datastore = None

def create_app():
    global security, user_datastore

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Register all blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    from app.routes.staff_routes import staff_bp
    app.register_blueprint(staff_bp, url_prefix="/api/staff")

    return app, user_datastore