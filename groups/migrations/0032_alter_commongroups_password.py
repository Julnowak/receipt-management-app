# Generated by Django 4.2.4 on 2023-10-04 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0031_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='=)BE8qCVfzG(eUtqm<wO', max_length=200),
        ),
    ]
