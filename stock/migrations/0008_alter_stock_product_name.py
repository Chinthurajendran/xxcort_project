# Generated by Django 5.0.2 on 2024-03-05 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_alter_stock_total_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='product_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
