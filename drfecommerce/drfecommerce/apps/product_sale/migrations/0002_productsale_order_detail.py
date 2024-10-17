# Generated by Django 4.2.15 on 2024-10-17 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("order_detail", "0003_remove_orderdetail_deleted_at_orderdetail_delete_at"),
        ("product_sale", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productsale",
            name="order_detail",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="order_detail.orderdetail",
            ),
            preserve_default=False,
        ),
    ]
