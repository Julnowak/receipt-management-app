# Generated by Django 4.2.4 on 2023-09-29 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0019_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='group_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='I7Wkg+8%hhGU)93k0(zZ', max_length=200),
        ),
    ]
