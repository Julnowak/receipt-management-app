# Generated by Django 4.2.4 on 2023-10-13 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_lists', '0008_product_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
    ]
