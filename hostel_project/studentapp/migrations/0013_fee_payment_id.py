# Generated by Django 5.1.4 on 2025-01-09 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0012_alter_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='fee',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
