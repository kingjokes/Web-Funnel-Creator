# Generated by Django 4.0.6 on 2022-11-01 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appauth', '0003_user_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(default='regular', max_length=12),
        ),
    ]
