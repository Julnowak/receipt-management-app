# Generated by Django 4.2.4 on 2023-10-13 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0005_remove_guarantee_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantee',
            name='end_date',
            field=models.DateTimeField(),
        ),
    ]
