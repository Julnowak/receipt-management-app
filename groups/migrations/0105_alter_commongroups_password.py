# Generated by Django 4.2.4 on 2023-11-05 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0104_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='mcQ2JM<cOiEoH5dR0>=%', max_length=200),
        ),
    ]
