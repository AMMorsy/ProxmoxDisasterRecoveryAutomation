import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dr_automation.settings")
app = Celery("dr_automation")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
