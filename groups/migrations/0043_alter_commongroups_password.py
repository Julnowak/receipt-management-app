# Generated by Django 4.2.4 on 2023-10-06 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0042_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='9?Pbc$cbJ7<yFU2b/yTR', max_length=200),
        ),
    ]
