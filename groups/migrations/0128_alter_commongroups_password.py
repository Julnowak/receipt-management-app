# Generated by Django 4.2.4 on 2023-11-19 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0127_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='>a&6zuaXb=Q%dIIN6P3!', max_length=200),
        ),
    ]