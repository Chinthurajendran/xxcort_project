# Generated by Django 5.0.2 on 2024-03-26 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0015_remove_order_list_coupon_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_list',
            name='coupon_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order_list',
            name='image',
            field=models.ImageField(null=True, upload_to='image'),
        ),
        migrations.AddField(
            model_name='order_list',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order_list',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]
