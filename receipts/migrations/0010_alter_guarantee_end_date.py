# Generated by Django 4.2.4 on 2023-10-26 00:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0009_listproduct_receipt_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantee',
            name='end_date',
            field=models.DateField(default=datetime.date(2023, 10, 26)),
        ),
    ]
