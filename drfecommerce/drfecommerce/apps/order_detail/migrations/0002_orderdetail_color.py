# Generated by Django 4.2.15 on 2024-12-01 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("order_detail", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderdetail",
            name="color",
            field=models.CharField(blank=True, default="", max_length=50, null=True),
        ),
    ]
