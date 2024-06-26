# Generated by Django 5.0.2 on 2024-03-04 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='offer',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='products',
            name='offer_price',
            field=models.DecimalField(decimal_places=3, default=None, max_digits=7),
        ),
    ]
