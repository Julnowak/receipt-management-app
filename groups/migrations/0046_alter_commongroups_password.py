# Generated by Django 4.2.4 on 2023-10-06 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0045_alter_commongroups_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commongroups',
            name='password',
            field=models.CharField(default='=%eY*36tqi>d$XtuUW!f', max_length=200),
        ),
    ]
