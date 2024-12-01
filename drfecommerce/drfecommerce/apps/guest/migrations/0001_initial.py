# Generated by Django 4.2.15 on 2024-11-03 16:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Guest",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("email", models.CharField(max_length=255, unique=True)),
                (
                    "address",
                    models.CharField(blank=True, default="", max_length=255, null=True),
                ),
                (
                    "city",
                    models.CharField(blank=True, default="", max_length=255, null=True),
                ),
                (
                    "country",
                    models.CharField(blank=True, default="", max_length=255, null=True),
                ),
                (
                    "postcode",
                    models.CharField(blank=True, default="", max_length=255, null=True),
                ),
                ("password", models.CharField(max_length=255)),
                (
                    "phone_number",
                    models.CharField(blank=True, default="", max_length=20, null=True),
                ),
                (
                    "avatar",
                    models.CharField(blank=True, default="", max_length=255, null=True),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "delete_at",
                    models.DateTimeField(blank=True, default=None, null=True),
                ),
            ],
            options={
                "db_table": "guests",
            },
        ),
    ]
