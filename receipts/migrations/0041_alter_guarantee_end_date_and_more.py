# Generated by Django 4.2.4 on 2023-11-23 22:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0040_alter_guarantee_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantee',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2023, 11, 23, 23, 9, 8, 617811)),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='date_of_receipt_bought',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 11, 23, 23, 9, 8, 615806), null=True),
        ),
    ]
