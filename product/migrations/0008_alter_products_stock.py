# Generated by Django 5.0.2 on 2024-03-05 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_products_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='stock',
            field=models.IntegerField(),
        ),
    ]
