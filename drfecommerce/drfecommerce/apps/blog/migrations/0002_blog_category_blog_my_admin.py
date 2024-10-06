# Generated by Django 4.2.15 on 2024-10-06 06:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("my_admin", "0001_initial"),
        ("category", "0001_initial"),
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="blog",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="category.category",
            ),
        ),
        migrations.AddField(
            model_name="blog",
            name="my_admin",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="my_admin.myadmin",
            ),
        ),
    ]
