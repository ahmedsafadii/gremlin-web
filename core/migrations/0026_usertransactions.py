# Generated by Django 4.1.7 on 2023-02-26 07:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0025_remove_plan_words_amount_plan_is_gift_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserTransactions",
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
                (
                    "amount",
                    models.IntegerField(
                        blank=True, default=0, null=True, verbose_name="Amount"
                    ),
                ),
                (
                    "is_credit",
                    models.BooleanField(default=0, null=True, verbose_name="Is credit"),
                ),
                ("notes", models.TextField(null=True, verbose_name="Notes")),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        null=True,
                        verbose_name="Created",
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, null=True, verbose_name="Updated"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "User Plan",
                "verbose_name_plural": "Users Plans",
            },
        ),
    ]
