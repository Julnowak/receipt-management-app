# Generated by Django 4.2.4 on 2023-10-24 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0090_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='znok+@D+p4=Yld/Swe%q', max_length=200),
        ),
    ]
