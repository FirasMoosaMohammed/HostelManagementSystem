# Generated by Django 5.1.4 on 2025-01-13 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentapp', '0017_alter_fee_razorpay_payment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fee',
            name='description',
            field=models.TextField(default='paid'),
        ),
    ]