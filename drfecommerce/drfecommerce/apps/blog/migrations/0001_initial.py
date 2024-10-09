# Generated by Django 4.2.15 on 2024-10-06 06:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Blog",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255)),
                ("short_description", models.TextField()),
                ("content", models.TextField()),
                ("status", models.CharField(max_length=50)),
                ("image", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]