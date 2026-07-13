from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required, current_user
from app.models import db, Trek, Booking, User
from app import cache

user_bp = Blueprint("user", __name__)


def trek_to_dict(trek):
    return {
        "id":              trek.id,
        "name":            trek.name,
        "location":        trek.location,
        "difficulty":      trek.difficulty,
        "duration_days":   trek.duration_days,
        "available_slots": trek.available_slots,
        "total_slots":     trek.total_slots,
        "status":          trek.status,
        "start_date":      str(trek.start_date) if trek.start_date else None,
        "end_date":        str(trek.end_date) if trek.end_date else None,
        "description":     trek.description,
    }


def booking_to_dict(booking):
    return {
        "id":             booking.id,
        "trek_id":        booking.trek_id,
        "trek_name":      booking.trek.name,
        "trek_location":  booking.trek.location,
        "booking_date":   str(booking.booking_date),
        "status":         booking.status,
        "payment_status": booking.payment_status,
        "trek_status":    booking.trek.status,
        "start_date":     str(booking.trek.start_date) if booking.trek.start_date else None,
        "end_date":       str(booking.trek.end_date) if booking.trek.end_date else None,
    }


# ── Dashboard ─────────────────────────────────────────────────────────────────

@user_bp.route("/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def dashboard():
    open_treks = Trek.query.filter_by(status="Open").all()

    my_bookings = Booking.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        "username":       current_user.username,
        "full_name":      current_user.full_name,
        "open_treks":     [trek_to_dict(t) for t in open_treks],
        "my_bookings":    [booking_to_dict(b) for b in my_bookings],
        "total_bookings": len(my_bookings),
    }), 200


# ── Browse available treks ────────────────────────────────────────────────────

@user_bp.route("/treks", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
@user_bp.route("/treks", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
@cache.cached(timeout=120, query_string=True) 

def browse_treks():
    search     = request.args.get("search", "").lower()
    difficulty = request.args.get("difficulty", "")
    location   = request.args.get("location", "").lower()
    duration   = request.args.get("duration_days")

    treks = Trek.query.filter_by(status="Open").all()

    if search:
        treks = [t for t in treks if search in t.name.lower()
                 or search in t.location.lower()]

    if difficulty:
        treks = [t for t in treks if t.difficulty == difficulty]

    if location:
        treks = [t for t in treks if location in t.location.lower()]

    if duration:
        treks = [t for t in treks if t.duration_days == int(duration)]

    return jsonify({"treks": [trek_to_dict(t) for t in treks]}), 200


# ── Book a trek ───────────────────────────────────────────────────────────────

@user_bp.route("/treks/<int:trek_id>/book", methods=["POST"])
@auth_required("token")
@roles_required("trekker")
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return jsonify({"message": "This trek is not open for booking"}), 400

    if trek.available_slots <= 0:
        return jsonify({"message": "No slots available for this trek"}), 400

    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek_id,
        status="Booked"
    ).first()
    if existing:
        return jsonify({"message": "You have already booked this trek"}), 409

    booking = Booking(
        user_id = current_user.id,
        trek_id = trek_id,
        status  = "Booked",
    )
    db.session.add(booking)

    trek.available_slots -= 1
    db.session.commit()

    return jsonify({
        "message": "Trek booked successfully!",
        "booking": booking_to_dict(booking),
    }), 201


# ── Cancel a booking ──────────────────────────────────────────────────────────

@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@auth_required("token")
@roles_required("trekker")
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return jsonify({"message": "This is not your booking"}), 403

    if booking.status != "Booked":
        return jsonify({"message": "Only active bookings can be cancelled"}), 400

    booking.status = "Cancelled"

    booking.trek.available_slots += 1
    db.session.commit()

    return jsonify({"message": "Booking cancelled successfully"}), 200


# ── View booking history ──────────────────────────────────────────────────────

@user_bp.route("/bookings", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def booking_history():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "bookings": [booking_to_dict(b) for b in bookings],
        "total":    len(bookings),
    }), 200


# ── View single booking ───────────────────────────────────────────────────────

@user_bp.route("/bookings/<int:booking_id>", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def get_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return jsonify({"message": "This is not your booking"}), 403

    return jsonify({"booking": booking_to_dict(booking)}), 200


# ── Edit profile ──────────────────────────────────────────────────────────────

@user_bp.route("/profile", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def get_profile():
    return jsonify({
        "id":        current_user.id,
        "email":     current_user.email,
        "username":  current_user.username,
        "full_name": current_user.full_name,
        "phone":     current_user.phone,
    }), 200


@user_bp.route("/profile", methods=["PUT"])
@auth_required("token")
@roles_required("trekker")
def update_profile():
    data = request.get_json()
    user = User.query.get(current_user.id)

    user.full_name = data.get("full_name", user.full_name)
    user.phone     = data.get("phone",     user.phone)

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200