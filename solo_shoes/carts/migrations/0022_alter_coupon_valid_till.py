# Generated by Django 4.1 on 2023-12-31 11:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0021_rename_shipping_address_cart_shipping_address_for_orders_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 30, 11, 40, 57, 7596, tzinfo=datetime.timezone.utc)),
        ),
    ]
