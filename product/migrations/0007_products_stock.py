# Generated by Django 5.0.2 on 2024-03-05 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_products_code_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='stock',
            field=models.IntegerField(default=None),
        ),
    ]
