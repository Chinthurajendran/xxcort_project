# Generated by Django 5.0.2 on 2024-03-05 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_stock_product_name_alter_stock_product_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stock',
            old_name='Extra_Large',
            new_name='extra_Large',
        ),
        migrations.RenameField(
            model_name='stock',
            old_name='Large',
            new_name='large',
        ),
        migrations.RenameField(
            model_name='stock',
            old_name='Medium',
            new_name='medium',
        ),
        migrations.RenameField(
            model_name='stock',
            old_name='Small',
            new_name='small',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='Total_Stock',
        ),
    ]
