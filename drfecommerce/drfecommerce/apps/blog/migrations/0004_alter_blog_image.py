# Generated by Django 4.2.15 on 2024-10-07 16:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0003_remove_blog_deleted_at_blog_delete_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="blog",
            name="image",
            field=models.CharField(blank=True, default="", max_length=255, null=True),
        ),
    ]
