# Generated by Django 4.2.4 on 2023-11-02 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_lists', '0016_remove_listproduct_selected_list_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppinglist',
            name='products',
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='products',
            field=models.ManyToManyField(to='shopping_lists.listproduct'),
        ),
    ]
