from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required, current_user
from app.models import db, Trek, Booking, StaffProfile

staff_bp = Blueprint("staff", __name__)

def trek_to_dict(trek):
    return {
        "id":               trek.id,
        "name":             trek.name,
        "location":         trek.location,
        "difficulty":       trek.difficulty,
        "duration_days":    trek.duration_days,
        "available_slots":  trek.available_slots,
        "total_slots":      trek.total_slots,
        "status":           trek.status,
        "start_date":       str(trek.start_date) if trek.start_date else None,
        "end_date":         str(trek.end_date) if trek.end_date else None,
        "description":      trek.description,
    }


def get_staff_profile():
    return StaffProfile.query.filter_by(user_id=current_user.id).first()


#dashboard route

@staff_bp.route("/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("trek_staff")
def dashboard():
    profile = get_staff_profile()
    if not profile:
        return jsonify({"message": "Staff profile not found"}), 404

    assigned = profile.assigned_treks
    summary  = []

    for trek in assigned:
        booked_count = Booking.query.filter_by(
            trek_id=trek.id, status="Booked"
        ).count()
        summary.append({
            **trek_to_dict(trek),
            "registered_trekkers": booked_count,
        })

    return jsonify({
        "staff_name":     current_user.full_name,
        "assigned_treks": summary,
    }), 200


#treks routes

@staff_bp.route("/treks", methods=["GET"])
@auth_required("token")
@roles_required("trek_staff")
def get_assigned_treks():
    profile = get_staff_profile()
    if not profile:
        return jsonify({"message": "Staff profile not found"}), 404

    treks = [trek_to_dict(t) for t in profile.assigned_treks]
    return jsonify({"treks": treks}), 200


#route for updating trek details

@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@auth_required("token")
@roles_required("trek_staff")
def update_trek(trek_id):
    profile = get_staff_profile()
    if not profile:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != profile.id:
        return jsonify({"message": "You are not assigned to this trek"}), 403

    data = request.get_json()

    if "available_slots" in data:
        new_slots = int(data["available_slots"])
        if new_slots < 0 or new_slots > trek.total_slots:
            return jsonify({"message": "Invalid slot count"}), 400
        trek.available_slots = new_slots

    if "status" in data:
        allowed = ["Open", "Closed", "Ongoing", "Completed"]
        if data["status"] not in allowed:
            return jsonify({"message": f"Status must be one of {allowed}"}), 400
        trek.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Trek updated", "trek": trek_to_dict(trek)}), 200


#View participants for an assigned trek 

@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@auth_required("token")
@roles_required("trek_staff")
def get_participants(trek_id):
    profile = get_staff_profile()
    if not profile:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != profile.id:
        return jsonify({"message": "You are not assigned to this trek"}), 403

    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    participants = [{
        "booking_id":     b.id,
        "user_id":        b.user_id,
        "name":           b.trekker.full_name,
        "email":          b.trekker.email,
        "booking_date":   str(b.booking_date),
        "status":         b.status,
        "payment_status": b.payment_status,
    } for b in bookings]

    return jsonify({
        "trek":         trek_to_dict(trek),
        "participants": participants,
        "total":        len(participants),
    }), 200


#Mark trek as started/completed

@staff_bp.route("/treks/<int:trek_id>/mark-started", methods=["POST"])
@auth_required("token")
@roles_required("trek_staff")
def mark_started(trek_id):
    profile = get_staff_profile()
    trek    = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != profile.id:
        return jsonify({"message": "You are not assigned to this trek"}), 403

    trek.status = "Ongoing"
    db.session.commit()
    return jsonify({"message": f"Trek '{trek.name}' marked as Ongoing"}), 200


@staff_bp.route("/treks/<int:trek_id>/mark-completed", methods=["POST"])
@auth_required("token")
@roles_required("trek_staff")
def mark_completed(trek_id):
    profile = get_staff_profile()
    trek    = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != profile.id:
        return jsonify({"message": "You are not assigned to this trek"}), 403

    trek.status = "Completed"

    active_bookings = Booking.query.filter_by(trek_id=trek_id, status="Booked").all()
    for booking in active_bookings:
        booking.status = "Completed"

    db.session.commit()
    return jsonify({"message": f"Trek '{trek.name}' marked as Completed"}), 200