# Generated by Django 4.2.4 on 2023-11-02 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0096_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='bATwf8C2MhnJ?jIisp@L', max_length=200),
        ),
    ]
