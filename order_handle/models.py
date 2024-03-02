from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator

# Create your models here.
class Shipment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    encryption_status = models.CharField(default='no',max_length=4)
    shipment_id = models.JSONField(default=dict)
    tracking_code = models.CharField(default = '',max_length=255)
    from_address = models.JSONField(default=dict)
    to_address = models.JSONField(default=dict)
    parcel = models.JSONField(default=dict)
    sub_status = models.CharField(default = '',null=True,max_length=255)
    main_status = models.CharField(default = '',null=True,max_length=255)

    updated=models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-updated','-created']

    def __str__(self):
        return f"Shipment {self.shipment_id}"

# Create your models here.
class Payment_handle(models.Model): 
    user = models.ForeignKey(User, null = True ,on_delete=models.CASCADE)
    shipment_id = models.CharField(default = '',null=True,max_length=255)
    rate_id = models.CharField(default = '',null=True,max_length=255)
    tracking_code = models.CharField(default = '',max_length=255)
    transaction_id = models.CharField(default = '',max_length=255)
    status = models.CharField(default = '',null=True,max_length=10)
    

    updated=models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-updated','-created']

    def __str__(self):
        return f"Shipment {self.shipment_id}"
    
class Processing_Fee(models.Model):
    fee = models.FloatField(validators = [MinValueValidator(0.1)])

    def __str__(self):
        return f'processing fee is : {self.fee}'
    

    

