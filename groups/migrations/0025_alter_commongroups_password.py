# Generated by Django 4.2.4 on 2023-10-04 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0024_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='H.iI43b.@KjT<GqQ!(MO', max_length=200),
        ),
    ]