# Generated by Django 4.2.4 on 2023-11-05 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_lists', '0019_remove_shoppinglist_products_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppinglist',
            name='display_only',
            field=models.BooleanField(default=False),
        ),
    ]
