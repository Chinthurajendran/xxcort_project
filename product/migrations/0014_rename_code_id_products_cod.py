# Generated by Django 5.0.2 on 2024-03-10 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_alter_products_code_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='products',
            old_name='code_id',
            new_name='cod',
        ),
    ]
