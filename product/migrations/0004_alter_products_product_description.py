# Generated by Django 5.0.2 on 2024-03-05 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_products_offer_price_alter_products_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='product_description',
            field=models.CharField(max_length=500),
        ),
    ]
