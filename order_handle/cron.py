from django_cron import CronJobBase, Schedule
from django.utils import timezone
from .models import Shipment

class MyCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=1440)  # Run every 24 hours
    code = 'order_handle.my_cron_job'  # Add this line

    def do(self):
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        Shipment.objects.filter(created__lt=thirty_days_ago).delete()
        print('checking and deleting data older than 30 days')
