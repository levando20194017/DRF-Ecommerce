# Generated by Django 4.2.15 on 2024-10-17 15:04

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("store", "0003_alter_store_postal_code"),
        ("product", "0004_alter_product_promotion"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductImcoming",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("cost_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity_in", models.IntegerField()),
                (
                    "vat",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "shipping_cost",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ("effective_date", models.DateTimeField(auto_now_add=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delete_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="product.product",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="store.store"
                    ),
                ),
            ],
        ),
    ]
