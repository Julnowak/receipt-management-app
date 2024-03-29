# Generated by Django 4.2.4 on 2023-12-03 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('promotions_and_discounts', '0010_remove_shop_slug_shop_category_shop_promos_available_and_more'),
        ('receipts', '0045_expense_is_deleted_guarantee_is_deleted_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='promotions_and_discounts.shop'),
        ),
    ]
