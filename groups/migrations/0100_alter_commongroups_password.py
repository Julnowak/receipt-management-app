# Generated by Django 4.2.4 on 2023-11-04 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0099_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='o=495X3F?u1tVaZ<Gafv', max_length=200),
        ),
    ]
