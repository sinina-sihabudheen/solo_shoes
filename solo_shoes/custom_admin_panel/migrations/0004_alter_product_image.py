# Generated by Django 4.2.4 on 2023-11-08 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin_panel', '0003_alter_product_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='adminside\x07ssets\\images\\solo_images'),
        ),
    ]
