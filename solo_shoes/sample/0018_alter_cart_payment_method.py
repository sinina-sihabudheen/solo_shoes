# Generated by Django 4.2.7 on 2023-12-11 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0017_coupon_alter_cart_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('COD', 'Cash on Delivery'), ('RAZ', 'Paid With Razorpay'), ('WAL', 'Paid with Wallet')], max_length=20, null=True),
        ),
    ]
