# Generated by Django 5.0.2 on 2024-03-06 06:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=50)),
                ('locality', models.CharField(max_length=20)),
                ('pincode', models.IntegerField()),
                ('district', models.CharField(max_length=14)),
                ('state', models.CharField(max_length=15)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.userdata')),
            ],
        ),
    ]
