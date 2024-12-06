# Generated by Django 4.2.15 on 2024-12-05 18:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("full_name", models.CharField(max_length=255)),
                ("email", models.CharField(blank=True, max_length=255, null=True)),
                ("phone_number", models.CharField(max_length=20)),
                ("question", models.TextField(max_length=1000)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "contacts",
            },
        ),
    ]
