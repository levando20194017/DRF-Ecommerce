# Generated by Django 4.2.15 on 2024-10-06 06:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BlogTag",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]