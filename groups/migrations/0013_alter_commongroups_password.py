# Generated by Django 4.2.4 on 2023-09-25 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0012_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='pLNsoB*8w-q9rs@u/z.+', max_length=200),
        ),
    ]