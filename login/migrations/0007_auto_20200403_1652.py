# Generated by Django 3.0.4 on 2020-04-03 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0006_auto_20200331_0139'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booked',
            old_name='Booking_id',
            new_name='booking_id',
        ),
    ]
