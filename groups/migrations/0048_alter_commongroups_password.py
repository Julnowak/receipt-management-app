# Generated by Django 4.2.4 on 2023-10-06 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0047_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='i9.p612&MCOb9XnTgB&U', max_length=200),
        ),
    ]