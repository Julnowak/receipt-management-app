# Generated by Django 4.2.4 on 2023-10-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0009_subcategories_icon_alter_basecategories_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basecategories',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
    ]
