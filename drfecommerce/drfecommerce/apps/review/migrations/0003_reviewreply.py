# Generated by Django 4.2.15 on 2024-10-22 15:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("my_admin", "0003_alter_myadmin_azure_ad"),
        ("review", "0002_review_store"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReviewReply",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("reply", models.TextField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "admin",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="my_admin.myadmin",
                    ),
                ),
                (
                    "review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="review.review"
                    ),
                ),
            ],
        ),
    ]