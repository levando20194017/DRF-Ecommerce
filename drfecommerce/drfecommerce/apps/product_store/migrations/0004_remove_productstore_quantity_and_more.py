# Generated by Django 4.2.15 on 2024-10-17 15:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "product_store",
            "0003_productstore_created_at_productstore_delete_at_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="productstore",
            name="quantity",
        ),
        migrations.AddField(
            model_name="productstore",
            name="quantity_in",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="productstore",
            name="remaining_stock",
            field=models.IntegerField(default=0),
        ),
    ]
