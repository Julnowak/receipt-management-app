# Generated by Django 4.2.4 on 2023-11-03 21:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0013_alter_guarantee_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantee',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 11, 3)),
        ),
    ]