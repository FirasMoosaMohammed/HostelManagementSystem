# Generated by Django 5.1.4 on 2024-12-29 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0011_alter_room_room_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_date',
            field=models.DateField(null=True),
        ),
    ]
