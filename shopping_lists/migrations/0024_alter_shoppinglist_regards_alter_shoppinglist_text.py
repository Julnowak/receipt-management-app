# Generated by Django 4.2.4 on 2024-01-07 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_lists', '0023_alter_shoppinglist_regards'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppinglist',
            name='regards',
            field=models.TextField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='text',
            field=models.CharField(max_length=150),
        ),
    ]
