# Generated by Django 4.2.4 on 2023-11-18 23:08

import datetime
from django.db import migrations, models
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0023_alter_guarantee_end_date'),
    ]

    operations = [
        TrigramExtension(),
    ]