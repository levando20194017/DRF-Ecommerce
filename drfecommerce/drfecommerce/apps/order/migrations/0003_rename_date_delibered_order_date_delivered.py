# Generated by Django 4.2.15 on 2024-12-05 11:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0002_order_date_cancelled_order_date_confirmed_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="date_delibered",
            new_name="date_delivered",
        ),
    ]
