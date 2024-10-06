# Generated by Django 4.2.15 on 2024-10-06 06:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Promotion",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("code", models.CharField(max_length=50)),
                ("from_date", models.DateField()),
                ("to_date", models.DateField()),
                ("special_price", models.FloatField()),
                ("member_price", models.FloatField()),
                ("rate", models.FloatField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
