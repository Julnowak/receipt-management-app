# Generated by Django 4.2.4 on 2023-10-06 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
