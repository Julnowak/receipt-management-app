# Generated by Django 4.2.4 on 2023-10-06 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0033_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='0OX3!Z<V-?Hxz*(nl57)', max_length=200),
        ),
    ]