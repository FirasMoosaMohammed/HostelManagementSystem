# Generated by Django 5.1.4 on 2025-01-12 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0013_fee_payment_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fee',
            old_name='payment_id',
            new_name='razorpay_order_id',
        ),
        migrations.AddField(
            model_name='fee',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
