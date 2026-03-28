"""
Celery configuration for BlogEngine project.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("blogengine")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "publish-scheduled-posts": {
        "task": "apps.posts.tasks.publish_scheduled_posts",
        "schedule": crontab(minute="*/1"),
    },
    "send-scheduled-newsletters": {
        "task": "apps.newsletter.tasks.send_scheduled_newsletters",
        "schedule": crontab(minute="*/5"),
    },
    "aggregate-daily-analytics": {
        "task": "apps.analytics.tasks.aggregate_daily_analytics",
        "schedule": crontab(hour=1, minute=0),
    },
    "cleanup-old-revisions": {
        "task": "apps.posts.tasks.cleanup_old_revisions",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
