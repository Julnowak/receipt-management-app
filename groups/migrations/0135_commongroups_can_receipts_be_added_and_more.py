# Generated by Django 4.2.4 on 2023-11-22 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0134_alter_commongroups_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='commongroups',
            name='can_receipts_be_added',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='commongroups',
            name='limit',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='LVS>TtmjSY)cFN%fL$.t', max_length=200),
        ),
    ]
