# Generated by Django 4.2.4 on 2023-11-04 01:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0014_alter_guarantee_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantee',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 11, 4)),
        ),
    ]
