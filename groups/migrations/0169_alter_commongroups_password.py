# Generated by Django 4.2.4 on 2024-01-09 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0168_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='h/oE/R28ehbJ-@mPR*ss', max_length=200),
        ),
    ]