# Generated by Django 4.2.4 on 2023-10-04 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0025_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='LyDoazqo4KLl+2D<u7/F', max_length=200),
        ),
    ]