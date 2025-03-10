# Generated by Django 4.2.15 on 2024-11-05 00:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0002_remove_product_audio_technologies_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="charging_port",
        ),
        migrations.RemoveField(
            model_name="product",
            name="charging_technology",
        ),
        migrations.RemoveField(
            model_name="product",
            name="os_version",
        ),
        migrations.AddField(
            model_name="product",
            name="charging",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="version",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
