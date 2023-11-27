# Generated by Django 4.2.4 on 2023-11-21 04:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0031_alter_guarantee_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='time_stamp',
            field=models.CharField(blank=True, choices=[('TYGODNI', 'Tygodni'), ('MIESIĘCY', 'Miesięcy'), ('LAT', 'Lat')], default='MIESIĘCY', max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='guarantee',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 11, 21)),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='date_of_receipt_bought',
            field=models.DateField(blank=True, default=datetime.date(2023, 11, 21), null=True),
        ),
    ]
