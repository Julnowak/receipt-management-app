# Generated by Django 4.2.4 on 2023-12-05 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0157_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='V/Yd?4yUdn.?UfW0ghnM', max_length=200),
        ),
    ]
