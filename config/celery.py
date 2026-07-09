import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "block_inactive_users_daily": {
        "task": "users.tasks.block_inactive_users",
        "schedule": crontab(hour=0, minute=0),
    },
}