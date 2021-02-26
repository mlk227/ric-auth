import datetime

from django.conf import settings
from django.utils import timezone

from celery import shared_task

from profiles.models import EmailReset


@shared_task()
def cron_job_expire_email_reset():
    try:
        email_reset_datetime = timezone.now() - datetime.timedelta(minutes=settings.EMAIL_RESET_EXPIRE_MINUTES)

        email_resets = EmailReset.objects.filter(is_deleted=False, created_at__lt=email_reset_datetime)
        email_resets.update(is_deleted=True)

    except Exception as e:
        print(str(timezone.now()), e)
