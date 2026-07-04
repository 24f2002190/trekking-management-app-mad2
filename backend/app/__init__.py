from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from app.models import db
from app.config import Config
from flask_security import Security, SQLAlchemyUserDatastore

security      = None
user_datastore = None
mail          = Mail()


def create_app():
    global security, user_datastore

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)

    from app.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Init Celery
    from app.celery_app import init_celery
    init_celery(app)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from app.routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    from app.routes.staff_routes import staff_bp
    app.register_blueprint(staff_bp, url_prefix="/api/staff")

    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    from app.routes.booking_routes import booking_bp
    app.register_blueprint(booking_bp, url_prefix="/api/bookings")

    from app.routes.job_routes import job_bp
    app.register_blueprint(job_bp, url_prefix="/api/jobs")

    return app, user_datastore