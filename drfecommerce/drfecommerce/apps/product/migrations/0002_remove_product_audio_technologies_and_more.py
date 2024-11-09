# Generated by Django 4.2.15 on 2024-11-04 16:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="audio_technologies",
        ),
        migrations.RemoveField(
            model_name="product",
            name="back_material",
        ),
        migrations.RemoveField(
            model_name="product",
            name="frame_material",
        ),
        migrations.RemoveField(
            model_name="product",
            name="gps_support",
        ),
        migrations.RemoveField(
            model_name="product",
            name="nfc",
        ),
        migrations.RemoveField(
            model_name="product",
            name="other_features",
        ),
        migrations.RemoveField(
            model_name="product",
            name="sim_type",
        ),
        migrations.RemoveField(
            model_name="product",
            name="telephoto_camera",
        ),
        migrations.RemoveField(
            model_name="product",
            name="ultra_wide_camera",
        ),
        migrations.RemoveField(
            model_name="product",
            name="water_resistance",
        ),
        migrations.AddField(
            model_name="product",
            name="other_info",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="bluetooth",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="camera_features",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="charging_port",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="charging_technology",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="network_support",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="os_version",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="screen_features",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="security_features",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="video_recording",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="wifi",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]