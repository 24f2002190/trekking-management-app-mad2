# Trekking Management Application V2

A web application built for the Modern Application Development II course at IIT Madras. The app helps adventure organizations manage treks, staff, and participant bookings through a role-based system.

---

## What this app does

Managing treks manually through spreadsheets and calls is messy. This application brings everything into one place — admins can create and manage treks, assign staff, and monitor all activity. Staff members handle their assigned treks and track participants. Trekkers can browse available treks, book them, and manage their history.

---

## Roles

**Admin** — has full access. Creates treks, manages staff and users, views all bookings and reports.

**Trek Staff** — sees only their assigned treks. Updates slots and status, views participant lists, marks treks as started or completed.

**Trekker** — self-registers. Browses open treks, books them, cancels if needed, and can export their history as a CSV.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask |
| Database | SQLite via SQLAlchemy |
| Authentication | Flask-Security-Too (token based) |
| Background Jobs | Celery + Redis |
| Caching | Flask-Caching + Redis |
| Email | Flask-Mail |
| Frontend | Vue.js 3 + Pinia + Vue Router |
| Styling | Bootstrap 5 |
| HTTP Client | Axios |

---

## Project Structure

```text
trekking-management-app-mad2/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # App factory, blueprint registration
│   │   ├── models.py           # Database models
│   │   ├── config.py           # Configuration
│   │   ├── celery_app.py       # Celery setup
│   │   ├── tasks.py            # Background tasks
│   │   └── routes/
│   │       ├── auth_routes.py
│   │       ├── admin_routes.py
│   │       ├── staff_routes.py
│   │       ├── user_routes.py
│   │       ├── booking_routes.py
│   │       └── job_routes.py
│   ├── run.py
│   ├── create_db.py
│   ├── celery_worker.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   ├── AdminView.vue
│   │   │   ├── StaffView.vue
│   │   │   └── TrekkerView.vue
│   │   ├── stores/
│   │   │   └── auth.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── api.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   └── package.json
└── README.md
```

## Prerequisites

Before running this, make sure you have the following installed:

- Python 3.11
- Node.js 18 or above
- Redis (must be running on localhost:6379)

To install and start Redis on Windows, download it from [here](https://github.com/microsoftarchive/redis/releases) and run it as a service. You can verify it is running by opening a terminal and typing: redis-cli ping

It should reply with `PONG`.

---

## Setup and Running

### 1. Clone the repository

```bash
git clone https://github.com/24f2002190/trekking-management-app-mad2.git
cd trekking-management-app-mad2
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
python create_db.py
```

The `create_db.py` script creates all the database tables and adds the default admin user.

Start the Flask server:

```bash
python run.py
```

The backend runs at `http://localhost:5000`

### 3. Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`

### 4. Celery worker

Open another terminal:

```bash
cd backend
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

### 5. Celery beat scheduler

Open one more terminal:

```bash
cd backend
celery -A celery_worker.celery beat --loglevel=info
```

---

## Default Login

Once you run `create_db.py`, the admin account is created automatically. No registration needed for admin.

Email:    admin@tma.com

Password: Admin@123

Trek staff accounts are created by the admin from the dashboard. Trekkers can self-register from the registration page.

---

## Background Jobs

The app runs three background jobs using Celery:

**Daily reminders** — sends an email to trekkers who have upcoming treks within 7 days. Runs automatically every 24 hours. Can also be triggered manually by admin.

**Monthly report** — generates an HTML report with trek statistics and emails it to the admin on the first of every month. Can also be triggered manually.

**CSV export** — trekkers can trigger this from their dashboard. It exports their full booking history as a CSV file and emails it to them. Runs asynchronously so the user does not have to wait.

---

## API Overview

All endpoints are prefixed with `/api`.

| Prefix | Who can access |
|---|---|
| `/api/auth` | Public |
| `/api/admin` | Admin only |
| `/api/staff` | Trek Staff only |
| `/api/user` | Trekkers only |
| `/api/bookings` | Role based |
| `/api/jobs` | Admin and Trekkers |

A full list of endpoints is in the project report.

---

## Notes

- The database file `tma.db` is not included in the repository. Run `python create_db.py` to generate it fresh.
- The `node_modules` folder is not included. Run `npm install` inside the `frontend` folder before starting.
- Email functionality requires a valid Gmail account with an App Password configured in `backend/app/config.py`.
- All demo data used in the video was created fresh using the application itself, no manual DB changes were made.

---

## Author

Vedika Agarwal

Roll Number: 24f2002190

IIT Madras BS in Data Science and Applications
