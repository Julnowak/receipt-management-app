# Generated by Django 4.2.4 on 2023-10-13 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0060_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='LrdK5(7QZBkJgPz2C9MS', max_length=200),
        ),
    ]