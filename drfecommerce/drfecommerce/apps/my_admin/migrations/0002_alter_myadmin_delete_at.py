# Generated by Django 4.2.15 on 2024-10-07 16:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("my_admin", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="myadmin",
            name="delete_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]