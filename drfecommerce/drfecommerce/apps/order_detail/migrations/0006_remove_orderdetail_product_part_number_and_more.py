# Generated by Django 4.2.15 on 2024-10-19 09:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order_detail", "0005_orderdetail_location_pickup"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderdetail",
            name="product_part_number",
        ),
        migrations.AlterField(
            model_name="orderdetail",
            name="product_code",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
