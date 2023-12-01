# Generated by Django 4.2.4 on 2023-11-20 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin_panel', '0008_size_productvariance'),
        ('carts', '0008_remove_whishlist_products_whishlist_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='whishlist',
            name='products',
        ),
        migrations.AddField(
            model_name='whishlist',
            name='products',
            field=models.ManyToManyField(related_name='wishlist_products', to='custom_admin_panel.product'),
        ),
    ]
