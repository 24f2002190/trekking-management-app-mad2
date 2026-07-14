from celery import Celery

celery = Celery(__name__)


def init_celery(app):
    celery.conf.update(
        broker_url       = app.config["CELERY_BROKER_URL"],
        result_backend   = app.config["CELERY_RESULT_BACKEND"],
        timezone         = app.config["CELERY_TIMEZONE"],
        beat_schedule    = {
            "daily-trek-reminders": {
                "task":     "app.tasks.send_daily_reminders",
                "schedule": 86400,   # every 24 hours in seconds
            },
            "monthly-admin-report": {
                "task":     "app.tasks.send_monthly_report",
                "schedule": 2592000, # every 30 days in seconds
            },
        }
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery