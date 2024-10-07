# Generated by Django 4.2.15 on 2024-10-06 06:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("guest", "0001_initial"),
        ("order", "0002_order_guest"),
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="guest",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="guest.guest",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="order.order",
            ),
        ),
    ]
