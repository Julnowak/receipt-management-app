# Generated by Django 4.2.4 on 2023-12-01 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0150_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='TcS?-s3Eg0EP&Y+2BM!@', max_length=200),
        ),
    ]