from flask import Blueprint, request, jsonify
from flask_security import auth_required, roles_required, current_user
from app.models import db, Trek, Booking, User, StaffProfile

booking_bp = Blueprint("booking", __name__)


def booking_to_dict(booking):
    return {
        "id":             booking.id,
        "user_id":        booking.user_id,
        "username":       booking.trekker.username,
        "full_name":      booking.trekker.full_name,
        "trek_id":        booking.trek_id,
        "trek_name":      booking.trek.name,
        "trek_location":  booking.trek.location,
        "trek_status":    booking.trek.status,
        "difficulty":     booking.trek.difficulty,
        "start_date":     str(booking.trek.start_date) if booking.trek.start_date else None,
        "end_date":       str(booking.trek.end_date) if booking.trek.end_date else None,
        "booking_date":   str(booking.booking_date),
        "status":         booking.status,
        "payment_status": booking.payment_status,
    }


# ── User: full trekking history ───────────────────────────────────────────────

@booking_bp.route("/my-history", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def my_trekking_history():
    """Complete history for the logged in trekker — all statuses."""
    status_filter = request.args.get("status")  # optional filter

    query = Booking.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.order_by(Booking.booking_date.desc()).all()

    return jsonify({
        "total":    len(bookings),
        "bookings": [booking_to_dict(b) for b in bookings],
    }), 200


# ── User: track a single booking status ──────────────────────────────────────

@booking_bp.route("/track/<int:booking_id>", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def track_booking(booking_id):
    """Let a trekker see the current status of one of their bookings."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return jsonify({"message": "This is not your booking"}), 403

    return jsonify({
        "booking":      booking_to_dict(booking),
        "trek_details": {
            "name":            booking.trek.name,
            "location":        booking.trek.location,
            "difficulty":      booking.trek.difficulty,
            "duration_days":   booking.trek.duration_days,
            "available_slots": booking.trek.available_slots,
            "current_status":  booking.trek.status,
        }
    }), 200


# ── Staff: view all bookings for their assigned treks ─────────────────────────

@booking_bp.route("/staff/trek/<int:trek_id>", methods=["GET"])
@auth_required("token")
@roles_required("trek_staff")
def staff_trek_bookings(trek_id):
    """Staff can see all bookings for a trek assigned to them."""
    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({"message": "Staff profile not found"}), 404

    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != profile.id:
        return jsonify({"message": "You are not assigned to this trek"}), 403

    status_filter = request.args.get("status")
    query         = Booking.query.filter_by(trek_id=trek_id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.all()

    return jsonify({
        "trek":     trek.name,
        "total":    len(bookings),
        "bookings": [booking_to_dict(b) for b in bookings],
    }), 200


# ── Admin: full historical records across all treks ───────────────────────────

@booking_bp.route("/admin/history", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_full_history():
    """Admin sees every booking ever made, with optional filters."""
    status_filter = request.args.get("status")
    trek_id       = request.args.get("trek_id")
    user_id       = request.args.get("user_id")

    query = Booking.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if trek_id:
        query = query.filter_by(trek_id=int(trek_id))
    if user_id:
        query = query.filter_by(user_id=int(user_id))

    bookings = query.order_by(Booking.booking_date.desc()).all()

    return jsonify({
        "total":    len(bookings),
        "bookings": [booking_to_dict(b) for b in bookings],
    }), 200


# ── Admin: trek status overview ───────────────────────────────────────────────

@booking_bp.route("/admin/trek-stats", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_trek_stats():
    """Admin gets a summary of all treks with booking counts."""
    treks  = Trek.query.all()
    result = []

    for trek in treks:
        total    = Booking.query.filter_by(trek_id=trek.id).count()
        booked   = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
        cancelled= Booking.query.filter_by(trek_id=trek.id, status="Cancelled").count()
        completed= Booking.query.filter_by(trek_id=trek.id, status="Completed").count()

        result.append({
            "trek_id":          trek.id,
            "trek_name":        trek.name,
            "location":         trek.location,
            "status":           trek.status,
            "total_slots":      trek.total_slots,
            "available_slots":  trek.available_slots,
            "total_bookings":   total,
            "active_bookings":  booked,
            "cancelled":        cancelled,
            "completed":        completed,
        })

    return jsonify({"trek_stats": result}), 200