# Generated by Django 5.0.2 on 2024-03-05 06:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_alter_products_stock'),
        ('stock', '0008_alter_stock_product_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='code_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stock.stock'),
        ),
    ]
