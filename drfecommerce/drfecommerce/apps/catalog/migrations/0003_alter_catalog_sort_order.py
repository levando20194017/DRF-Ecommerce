# Generated by Django 4.2.15 on 2024-10-11 13:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_remove_catalog_deleted_at_catalog_delete_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="catalog",
            name="sort_order",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
