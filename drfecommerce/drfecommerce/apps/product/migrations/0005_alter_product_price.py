# Generated by Django 4.2.15 on 2024-11-07 14:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0004_alter_product_color_alter_product_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.IntegerField(),
        ),
    ]
