# Generated by Django 4.2.15 on 2024-10-17 13:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("product_store", "0002_productstore_product_productstore_store"),
    ]

    operations = [
        migrations.AddField(
            model_name="productstore",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="productstore",
            name="delete_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="productstore",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
