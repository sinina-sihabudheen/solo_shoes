# Generated by Django 4.2.7 on 2023-12-09 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0013_remove_cartitem_variation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_items', to='carts.cart'),
        ),
    ]
