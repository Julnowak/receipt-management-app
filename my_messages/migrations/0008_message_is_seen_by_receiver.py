# Generated by Django 4.2.4 on 2023-11-04 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_messages', '0007_message_is_seen_by_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_seen_by_receiver',
            field=models.BooleanField(default=True),
        ),
    ]
