# Generated by Django 4.2.4 on 2023-11-23 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0138_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='EI%plJ=ay7UTB8Pdn@>0', max_length=200),
        ),
    ]
