# Generated by Django 4.2.4 on 2023-10-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0088_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='0n&e*Jb<5r?6VH1*3qPA', max_length=200),
        ),
    ]