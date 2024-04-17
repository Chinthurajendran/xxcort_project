# Generated by Django 5.0.2 on 2024-03-12 08:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0003_address2'),
    ]

    operations = [
        migrations.CreateModel(
            name='checkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.userdata')),
            ],
        ),
        migrations.CreateModel(
            name='order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(default='Pending', max_length=15)),
                ('payment_method', models.CharField(default='COD', max_length=15)),
                ('order_status', models.CharField(default='Pending', max_length=15)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('billing_address', models.CharField(max_length=50)),
                ('billing_locality', models.CharField(max_length=20)),
                ('billing_pincode', models.IntegerField()),
                ('billing_district', models.CharField(max_length=14)),
                ('billing_state', models.CharField(max_length=15)),
                ('shipping_address', models.CharField(max_length=50)),
                ('shipping_locality', models.CharField(max_length=20)),
                ('shipping_pincode', models.IntegerField()),
                ('shipping_district', models.CharField(max_length=14)),
                ('shipping_state', models.CharField(max_length=15)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.userdata')),
            ],
        ),
    ]
