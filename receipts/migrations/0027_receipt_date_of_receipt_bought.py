# Generated by Django 4.2.4 on 2023-11-19 03:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0026_alter_receipt_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='date_of_receipt_bought',
            field=models.DateField(default=datetime.date(2023, 11, 19)),
        ),
    ]