# Generated by Django 4.1 on 2023-12-31 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0008_shippingaddress_created_at_and_more'),
        ('carts', '0020_cart_coupon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='shipping_address',
            new_name='shipping_address_for_orders',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='delivery_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_profile.shippingaddress'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_name_at_order',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
