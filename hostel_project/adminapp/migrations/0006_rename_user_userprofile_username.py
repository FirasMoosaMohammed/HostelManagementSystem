# Generated by Django 5.1.4 on 2024-12-24 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0005_userprofile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='user',
            new_name='username',
        ),
    ]
