# Generated by Django 4.1 on 2024-01-03 07:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0032_alter_coupon_valid_till'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='valid_till',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 2, 7, 0, 0, 915211, tzinfo=datetime.timezone.utc)),
        ),
    ]
