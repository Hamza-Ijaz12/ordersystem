# Generated by Django 5.0.1 on 2024-02-28 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order_handle', '0006_precessing_fee'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Precessing_Fee',
            new_name='Processing_Fee',
        ),
    ]
