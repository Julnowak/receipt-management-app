# Generated by Django 4.2.4 on 2023-10-06 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0035_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='rsKVJk71/pgU?O.SGuZy', max_length=200),
        ),
    ]