# Generated by Django 5.1.4 on 2025-01-12 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0015_fee_razorpay_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='amount',
            field=models.IntegerField(),
        ),
    ]