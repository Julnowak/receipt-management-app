# Generated by Django 4.2.4 on 2023-09-25 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0016_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='jO&F&47P*=FfQaU=FU.I', max_length=200),
        ),
    ]
