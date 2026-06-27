from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    __tablename__ = "role"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    password      = db.Column(db.String(255), nullable=False)
    full_name     = db.Column(db.String(150))
    phone         = db.Column(db.String(20))
    active        = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Flask-Security relationship
    roles = db.relationship("Role", secondary=user_roles, backref="users")

    bookings      = db.relationship("Booking", backref="trekker", lazy=True)
    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Trek(db.Model):
    __tablename__ = "trek"

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(150), nullable=False)
    location        = db.Column(db.String(150), nullable=False)
    difficulty      = db.Column(db.String(20),  nullable=False)  
    duration_days   = db.Column(db.Integer,      nullable=False)
    available_slots = db.Column(db.Integer,      nullable=False)
    total_slots     = db.Column(db.Integer,      nullable=False)
    status          = db.Column(db.String(20),   default="Pending") 
    start_date      = db.Column(db.Date)
    end_date        = db.Column(db.Date)
    description     = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff_profile.id"), nullable=True)
    bookings = db.relationship("Booking", backref="trek", lazy=True)

    def __repr__(self):
        return f"<Trek {self.name} | {self.status}>"


class StaffProfile(db.Model):
    __tablename__ = "staff_profile"

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    contact_detail = db.Column(db.String(200))
    is_active      = db.Column(db.Boolean, default=True)
    joined_at      = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_treks = db.relationship("Trek", backref="assigned_staff", lazy=True, foreign_keys="Trek.assigned_staff_id")

    def __repr__(self):
        return f"<StaffProfile user_id={self.user_id}>"


class Booking(db.Model):
    __tablename__ = "booking"

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("user.id"),  nullable=False)
    trek_id        = db.Column(db.Integer, db.ForeignKey("trek.id"),  nullable=False)
    booking_date   = db.Column(db.DateTime, default=datetime.utcnow)
    status         = db.Column(db.String(20), default="Booked")   
    payment_status = db.Column(db.String(20), default="Pending")   

    def __repr__(self):
        return f"<Booking user={self.user_id} trek={self.trek_id} status={self.status}>"