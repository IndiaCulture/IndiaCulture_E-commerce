# Generated by Django 5.2.1 on 2025-06-07 10:45

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_remove_order_razorpay_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_screenshot',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='Payment Screenshot'),
        ),
    ]
