# Generated by Django 5.0.2 on 2024-03-26 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0006_order_list_image_order_list_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_list',
            name='coupon_price',
            field=models.IntegerField(default=0),
        ),
    ]
