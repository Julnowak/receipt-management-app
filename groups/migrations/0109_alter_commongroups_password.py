# Generated by Django 4.2.4 on 2023-11-06 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0108_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='TAP<2p0!FDH/jm10u(D)', max_length=200),
        ),
    ]
