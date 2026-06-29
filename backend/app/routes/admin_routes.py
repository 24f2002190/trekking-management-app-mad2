from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required
from app.models import db, User, Trek, Booking, StaffProfile, Role
from app import user_datastore
import uuid

admin_bp = Blueprint("admin", __name__)


def staff_to_dict(staff):
    return {
        "id": staff.id,
        "user_id": staff.user_id,
        "name": staff.user.full_name,
        "email": staff.user.email,
        "contact_detail": staff.contact_detail,
        "is_active": staff.is_active,
        "assigned_treks": [{"id": t.id, "name": t.name} for t in staff.assigned_treks]
    }


def trek_to_dict(trek):
    return {
        "id": trek.id,
        "name": trek.name,
        "location": trek.location,
        "difficulty": trek.difficulty,
        "duration_days": trek.duration_days,
        "available_slots": trek.available_slots,
        "total_slots": trek.total_slots,
        "status": trek.status,
        "start_date": str(trek.start_date) if trek.start_date else None,
        "end_date": str(trek.end_date) if trek.end_date else None,
        "description": trek.description,
        "assigned_staff_id": trek.assigned_staff_id,
    }


# ── Dashboard summary ────────────────────────────────────────────────────────

@admin_bp.route("/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def dashboard():
    total_treks    = Trek.query.count()
    total_bookings = Booking.query.count()
    total_staff    = StaffProfile.query.count()

    trekker_role   = Role.query.filter_by(name="trekker").first()
    total_trekkers = len(trekker_role.users) if trekker_role else 0

    return jsonify({
        "total_treks":    total_treks,
        "total_bookings": total_bookings,
        "total_staff":    total_staff,
        "total_trekkers": total_trekkers,
    }), 200


# ── Trek management ──────────────────────────────────────────────────────────

@admin_bp.route("/treks", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_all_treks():
    search = request.args.get("search", "").lower()
    treks  = Trek.query.all()
    if search:
        treks = [t for t in treks if search in t.name.lower() or search in t.location.lower()]
    return jsonify({"treks": [trek_to_dict(t) for t in treks]}), 200


@admin_bp.route("/treks", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def create_trek():
    data = request.get_json()

    required = ["name", "location", "difficulty", "duration_days", "total_slots"]
    for field in required:
        if not data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if data["difficulty"] not in ["Easy", "Moderate", "Hard"]:
        return jsonify({"message": "difficulty must be Easy, Moderate, or Hard"}), 400

    trek = Trek(
        name            = data["name"],
        location        = data["location"],
        difficulty      = data["difficulty"],
        duration_days   = int(data["duration_days"]),
        total_slots     = int(data["total_slots"]),
        available_slots = int(data["total_slots"]),
        status          = "Pending",
        description     = data.get("description", ""),
        start_date      = data.get("start_date"),
        end_date        = data.get("end_date"),
    )
    db.session.add(trek)
    db.session.commit()
    return jsonify({"message": "Trek created", "trek": trek_to_dict(trek)}), 201


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json()

    trek.name            = data.get("name",          trek.name)
    trek.location        = data.get("location",       trek.location)
    trek.difficulty      = data.get("difficulty",     trek.difficulty)
    trek.duration_days   = data.get("duration_days",  trek.duration_days)
    trek.total_slots     = data.get("total_slots",    trek.total_slots)
    trek.available_slots = data.get("available_slots",trek.available_slots)
    trek.status          = data.get("status",         trek.status)
    trek.description     = data.get("description",    trek.description)
    trek.start_date      = data.get("start_date",     trek.start_date)
    trek.end_date        = data.get("end_date",       trek.end_date)

    db.session.commit()
    return jsonify({"message": "Trek updated", "trek": trek_to_dict(trek)}), 200


@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@auth_required("token")
@roles_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    return jsonify({"message": "Trek deleted"}), 200


# ── Staff management ─────────────────────────────────────────────────────────

@admin_bp.route("/staff", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_all_staff():
    search = request.args.get("search", "").lower()
    staff_list = StaffProfile.query.all()
    if search:
        staff_list = [s for s in staff_list if search in s.user.full_name.lower()]
    return jsonify({"staff": [staff_to_dict(s) for s in staff_list]}), 200


@admin_bp.route("/staff", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def create_staff():
    data = request.get_json()

    required = ["email", "username", "password", "full_name"]
    for field in required:
        if not data.get(field):
            return jsonify({"message": f"{field} is required"}), 400

    if user_datastore.find_user(email=data["email"]):
        return jsonify({"message": "Email already exists"}), 409

    from flask_security import hash_password
    new_user = user_datastore.create_user(
        email         = data["email"],
        username      = data["username"],
        full_name     = data["full_name"],
        password      = hash_password(data["password"]),
        fs_uniquifier = str(uuid.uuid4()),
        roles         = ["trek_staff"],
    )
    db.session.flush()

    staff_profile = StaffProfile(
        user_id        = new_user.id,
        contact_detail = data.get("contact_detail", ""),
    )
    db.session.add(staff_profile)
    db.session.commit()

    return jsonify({"message": "Staff created", "staff": staff_to_dict(staff_profile)}), 201


@admin_bp.route("/staff/<int:staff_id>/assign/<int:trek_id>", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def assign_staff_to_trek(staff_id, trek_id):
    staff = StaffProfile.query.get_or_404(staff_id)
    trek  = Trek.query.get_or_404(trek_id)

    trek.assigned_staff_id = staff.id
    db.session.commit()
    return jsonify({"message": f"{staff.user.full_name} assigned to {trek.name}"}), 200


# ── User management ──────────────────────────────────────────────────────────

@admin_bp.route("/users", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_all_users():
    search       = request.args.get("search", "").lower()
    trekker_role = Role.query.filter_by(name="trekker").first()
    users        = trekker_role.users if trekker_role else []

    if search:
        users = [u for u in users if search in u.full_name.lower() or search in u.email.lower()]

    result = [{"id": u.id, "email": u.email, "username": u.username,
               "full_name": u.full_name, "active": u.active} for u in users]
    return jsonify({"users": result}), 200


@admin_bp.route("/users/<int:user_id>/deactivate", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.active = False
    db.session.commit()
    return jsonify({"message": f"{user.username} has been deactivated"}), 200


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.active = True
    db.session.commit()
    return jsonify({"message": f"{user.username} has been activated"}), 200


# ── Bookings overview ────────────────────────────────────────────────────────

@admin_bp.route("/bookings", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_all_bookings():
    bookings = Booking.query.all()
    result = [{
        "id":             b.id,
        "user":           b.trekker.username,
        "trek":           b.trek.name,
        "booking_date":   str(b.booking_date),
        "status":         b.status,
        "payment_status": b.payment_status,
    } for b in bookings]
    return jsonify({"bookings": result}), 200