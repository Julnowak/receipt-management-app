# Generated by Django 4.2.4 on 2023-10-06 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0051_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='XXM4Q%y8z2>nGrhQ@eoW', max_length=200),
        ),
    ]
