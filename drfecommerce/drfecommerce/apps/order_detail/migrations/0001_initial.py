# Generated by Django 4.2.15 on 2024-10-24 16:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("product", "0001_initial"),
        ("order", "0001_initial"),
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderDetail",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "product_code",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("product_name", models.CharField(max_length=255)),
                ("quantity", models.IntegerField()),
                ("unit_price", models.FloatField()),
                ("location_pickup", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delete_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="order.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="product.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="store.store",
                    ),
                ),
            ],
        ),
    ]
