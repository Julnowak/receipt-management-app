# Generated by Django 4.2.4 on 2023-10-17 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0077_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='Ji1atl?q?@$LQph&!?ow', max_length=200),
        ),
    ]
