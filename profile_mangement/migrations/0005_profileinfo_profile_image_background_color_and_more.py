# Generated by Django 4.2.4 on 2023-10-17 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile_mangement', '0004_profileinfo_is_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='profileinfo',
            name='profile_image_background_color',
            field=models.CharField(default='#FFFFFF', max_length=7),
        ),
        migrations.AddField(
            model_name='profileinfo',
            name='profile_image_color',
            field=models.CharField(default='#000000', max_length=7),
        ),
    ]
