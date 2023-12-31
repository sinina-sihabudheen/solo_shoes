# Generated by Django 4.2.4 on 2023-11-14 14:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
       
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_profile', '0001_initial'),
        ('custom_admin_panel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(default=django.utils.timezone.now)),
                ('complete', models.BooleanField(default=False, null=True)),
                ('payment_method', models.CharField(blank=True, choices=[('COD', 'Cash on Delivery')], max_length=20, null=True)),
                ('shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_profile.shippingaddress')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, default=0, null=True)),
                ('delivery_status', models.CharField(choices=[('PL', 'Order placed'), ('DS', 'Dispatched'), ('SH', 'Shipped'), ('OFD', 'Out for Delivery'), ('D', 'Delivered'), ('CN', 'Order Cancelled'), ('RT', 'Returned')], default='PL', max_length=3)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='carts.cart')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='custom_admin_panel.product')),
                
            ],
        ),
    ]
