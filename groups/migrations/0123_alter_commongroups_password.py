# Generated by Django 4.2.4 on 2023-11-19 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0122_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='qspUx<%aOLfGQQASHR2)', max_length=200),
        ),
    ]
