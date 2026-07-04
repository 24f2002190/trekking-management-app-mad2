from flask import Blueprint, jsonify
from flask_security import auth_required, roles_required, current_user
from app.tasks import send_daily_reminders, send_monthly_report, export_booking_csv

job_bp = Blueprint("jobs", __name__)


@job_bp.route("/trigger-reminders", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def trigger_reminders():
    """Admin can manually trigger the daily reminder job."""
    task = send_daily_reminders.delay()
    return jsonify({
        "message": "Daily reminder job triggered",
        "task_id": task.id,
    }), 202


@job_bp.route("/trigger-report", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def trigger_report():
    """Admin can manually trigger the monthly report."""
    task = send_monthly_report.delay()
    return jsonify({
        "message": "Monthly report job triggered",
        "task_id": task.id,
    }), 202


@job_bp.route("/export-csv", methods=["POST"])
@auth_required("token")
@roles_required("trekker")
def export_csv():
    """Trekker triggers their own CSV export."""
    task = export_booking_csv.delay(current_user.id)
    return jsonify({
        "message": "CSV export started, you will receive an email shortly",
        "task_id": task.id,
    }), 202


@job_bp.route("/task-status/<task_id>", methods=["GET"])
@auth_required("token")
def task_status(task_id):
    """Check status of any async task."""
    from app.celery_app import celery
    task = celery.AsyncResult(task_id)
    return jsonify({
        "task_id": task_id,
        "status":  task.status,
        "result":  str(task.result) if task.ready() else "still processing",
    }), 200