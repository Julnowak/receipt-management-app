# Generated by Django 4.2.4 on 2023-10-06 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0052_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='4sY$&=eiSFFiz$+(qU=@', max_length=200),
        ),
    ]
