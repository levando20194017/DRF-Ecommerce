# Generated by Django 4.2.15 on 2024-11-22 16:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("promotion", "0003_promotion_discount_type_promotion_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="promotion",
            name="member_price",
        ),
        migrations.RemoveField(
            model_name="promotion",
            name="rate",
        ),
        migrations.RemoveField(
            model_name="promotion",
            name="special_price",
        ),
    ]
