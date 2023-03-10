# Generated by Django 4.1.7 on 2023-02-28 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0044_plan_sub_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppleWebHook",
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
                ("get_body", models.TextField(default="", verbose_name="Get Body")),
                ("post_body", models.TextField(default="", verbose_name="Post Body")),
                ("error", models.TextField(default="", verbose_name="Error")),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="Created"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Updated"
                    ),
                ),
            ],
            options={
                "verbose_name": "Apple Web Hook",
                "verbose_name_plural": "Apple Web Hook",
            },
        ),
    ]
