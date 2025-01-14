# Generated by Django 5.1.4 on 2025-01-11 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0016_remove_notice_time_posted_alter_notice_date_posted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='occupied',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_number',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]