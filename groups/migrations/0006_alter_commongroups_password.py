# Generated by Django 4.2.4 on 2023-09-24 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0005_alter_commongroups_number_of_members_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='(IF0$p%VOwK0R$TM><q0', max_length=200),
        ),
    ]