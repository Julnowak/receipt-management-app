# Generated by Django 4.2.4 on 2023-10-13 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0061_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='4T27gyQKkVSmlmPYH88o', max_length=200),
        ),
    ]