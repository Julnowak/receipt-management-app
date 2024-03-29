# Generated by Django 4.2.4 on 2023-10-27 00:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0095_alter_commongroups_password'),
        ('shopping_lists', '0014_listproduct_by_who_shoppinglist_is_completed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppinglist',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='groups.commongroups'),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='realizators',
            field=models.ManyToManyField(default=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL), related_name='realizators', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='regards',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
