# Generated by Django 4.2.4 on 2023-10-16 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0068_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='?@UQm(RYfH1pYPtht9EV', max_length=200),
        ),
    ]
