# Generated by Django 4.2.4 on 2023-10-04 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_messages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='new',
            field=models.BooleanField(default=True),
        ),
    ]
