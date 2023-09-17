# Generated by Django 4.2.4 on 2023-08-20 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_lists', '0002_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='text',
        ),
        migrations.AddField(
            model_name='product',
            name='selected_list',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='shopping_lists.shoppinglist'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='product',
            field=models.CharField(max_length=200),
        ),
    ]