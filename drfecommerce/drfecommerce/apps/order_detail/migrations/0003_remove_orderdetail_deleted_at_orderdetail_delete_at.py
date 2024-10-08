# Generated by Django 4.2.15 on 2024-10-07 16:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order_detail", "0002_orderdetail_order_orderdetail_product"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderdetail",
            name="deleted_at",
        ),
        migrations.AddField(
            model_name="orderdetail",
            name="delete_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
