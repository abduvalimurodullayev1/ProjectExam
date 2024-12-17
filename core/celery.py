import os
from celery.schedules import crontab
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

app = Celery("core")
app.conf.beat_schedule = {
    'check-new-listings-every-10-minutes': {
        'task': 'apps.bot.tasks.scrape_and_save_listings',
        'schedule': crontab(minute='*/5'),
    },
}


app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
