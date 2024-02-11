# Generated by Django 4.2.2 on 2024-02-11 07:08

import authentication.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_alter_user_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, default='user.png', null=True, upload_to=authentication.models.upload_to),
        ),
    ]
