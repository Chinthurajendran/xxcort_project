# Generated by Django 5.0 on 2024-04-15 04:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_alter_cart_quantity'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CartItms',
        ),
    ]
