# Generated by Django 4.2.4 on 2023-09-25 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0017_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='YN-dL-fu5/fF*FI-Lub%', max_length=200),
        ),
    ]
