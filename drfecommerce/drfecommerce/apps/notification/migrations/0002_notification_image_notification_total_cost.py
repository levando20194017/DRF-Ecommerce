# Generated by Django 4.2.15 on 2024-12-05 13:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="image",
            field=models.CharField(blank=True, default="", max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="total_cost",
            field=models.FloatField(default=0),
        ),
    ]