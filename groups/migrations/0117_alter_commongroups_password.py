# Generated by Django 4.2.4 on 2023-11-18 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0116_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='GsW%8LMr2g$NxB&kY!lm', max_length=200),
        ),
    ]
