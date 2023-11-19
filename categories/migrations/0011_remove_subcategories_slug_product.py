# Generated by Django 4.2.4 on 2023-11-18 18:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0010_alter_basecategories_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subcategories',
            name='slug',
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('subcategory', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='categories.subcategories')),
            ],
            options={
                'verbose_name_plural': 'Subcategories',
            },
        ),
    ]
