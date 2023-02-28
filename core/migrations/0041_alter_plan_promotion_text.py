# Generated by Django 4.1.7 on 2023-02-28 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0040_alter_plan_promotion_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plan",
            name="promotion_text",
            field=models.TextField(
                blank=True,
                help_text="Use {{amount}} for amount",
                null=True,
                verbose_name="Promotion text",
            ),
        ),
    ]
