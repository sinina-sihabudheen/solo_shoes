# Generated by Django 4.2.4 on 2023-11-26 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin_panel', '0008_size_productvariance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='custom_admin_panel.product'),
        ),
    ]
