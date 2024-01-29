from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Create your models here.
class Shipment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    encryption_status = models.CharField(default='no',max_length=4)
    shipment_id = models.JSONField(default=dict)
    tracking_code = models.JSONField(default=dict)
    from_address = models.JSONField(default=dict)
    to_address = models.JSONField(default=dict)
    parcel = models.JSONField(default=dict)

    updated=models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-updated','-created']

    def __str__(self):
        return f"Shipment {self.shipment_id}"
    

    

