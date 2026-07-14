from app.celery_app import celery
from app.models import db, User, Trek, Booking, Role
from flask_mail import Message
from datetime import datetime
import csv
import io


def get_mail():
    from app import mail
    return mail


# ── Task 1: Daily reminder emails ─────────────────────────────────────────────

@celery.task(name="app.tasks.send_daily_reminders")
def send_daily_reminders():
    mail = get_mail()

    active_bookings = Booking.query.filter_by(status="Booked").all()
    count = 0

    for booking in active_bookings:
        trek = booking.trek
        user = booking.trekker

        if not trek.start_date:
            continue

        days_left = (trek.start_date - datetime.utcnow().date()).days

        if 0 <= days_left <= 7:
            try:
                msg = Message(
                    subject = f"Reminder: Your trek '{trek.name}' starts in {days_left} days!",
                    recipients = [user.email],
                    html = f"""
                        <h2>Trek Reminder</h2>
                        <p>Hi {user.full_name},</p>
                        <p>Your upcoming trek <strong>{trek.name}</strong> starts
                        in <strong>{days_left} days</strong>!</p>
                        <ul>
                            <li>Location: {trek.location}</li>
                            <li>Start Date: {trek.start_date}</li>
                            <li>Duration: {trek.duration_days} days</li>
                            <li>Difficulty: {trek.difficulty}</li>
                        </ul>
                        <p>Make sure you are well prepared. Happy trekking!</p>
                    """
                )
                mail.send(msg)
                count += 1
            except Exception as e:
                print(f"Failed to send reminder to {user.email}: {e}")

    return f"Sent {count} reminder emails"


# ── Task 2: Monthly admin report ──────────────────────────────────────────────

@celery.task(name="app.tasks.send_monthly_report")
def send_monthly_report():
    mail  = get_mail()
    now   = datetime.utcnow()
    month = now.strftime("%B %Y")

    treks     = Trek.query.all()
    bookings  = Booking.query.all()
    completed = Booking.query.filter_by(status="Completed").count()

    # Find most popular trek
    trek_counts = {}
    for b in bookings:
        trek_counts[b.trek.name] = trek_counts.get(b.trek.name, 0) + 1

    popular = max(trek_counts, key=trek_counts.get) if trek_counts else "N/A"

    # Build HTML report
    trek_rows = ""
    for trek in treks:
        count = Booking.query.filter_by(trek_id=trek.id).count()
        trek_rows += f"""
            <tr>
                <td>{trek.name}</td>
                <td>{trek.location}</td>
                <td>{trek.status}</td>
                <td>{count}</td>
            </tr>
        """

    html_report = f"""
        <h1>Monthly Trekking Report — {month}</h1>
        <h3>Summary</h3>
        <ul>
            <li>Total Treks: {len(treks)}</li>
            <li>Total Bookings: {len(bookings)}</li>
            <li>Completed Treks: {completed}</li>
            <li>Most Popular Trek: {popular}</li>
        </ul>
        <h3>Trek-wise Breakdown</h3>
        <table border="1" cellpadding="8">
            <tr>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Status</th>
                <th>Total Bookings</th>
            </tr>
            {trek_rows}
        </table>
        <p>Generated on {now.strftime("%d %B %Y at %H:%M UTC")}</p>
    """

    admin_role = Role.query.filter_by(name="admin").first()
    admin_user = admin_role.users[0] if admin_role and admin_role.users else None

    if admin_user:
        try:
            msg = Message(
                subject    = f"Monthly Trekking Report — {month}",
                recipients = [admin_user.email],
                html       = html_report,
            )
            mail.send(msg)
            return f"Monthly report sent to {admin_user.email}"
        except Exception as e:
            return f"Failed to send report: {e}"

    return "No admin found"


# ── Task 3: CSV export ──────────────────────────────────────

@celery.task(name="app.tasks.export_booking_csv")
def export_booking_csv(user_id):
    mail = get_mail()
    user = User.query.get(user_id)

    if not user:
        return "User not found"

    bookings = Booking.query.filter_by(user_id=user_id).all()

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Booking ID", "Trek Name", "Location",
        "Difficulty", "Start Date", "End Date",
        "Booking Date", "Booking Status", "Payment Status"
    ])

    for b in bookings:
        writer.writerow([
            b.id,
            b.trek.name,
            b.trek.location,
            b.trek.difficulty,
            b.trek.start_date,
            b.trek.end_date,
            b.booking_date.strftime("%Y-%m-%d"),
            b.status,
            b.payment_status,
        ])

    csv_content = output.getvalue()

    try:
        msg = Message(
            subject    = "Your Trekking History Export",
            recipients = [user.email],
            html       = f"""
                <h2>Your Trekking History </h2>
                <p>Hi {user.full_name},</p>
                <p>Please find your trekking history CSV attached.</p>
                <p>Total bookings: {len(bookings)}</p>
            """,
        )
        msg.attach(
            filename     = "trekking_history.csv",
            content_type = "text/csv",
            data         = csv_content,
        )
    
        mail.send(msg)
        return f"CSV exported and sent to {user.email}"
    except Exception as e:
        return f"Failed to send CSV: {e}"