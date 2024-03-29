# Generated by Django 4.1.7 on 2023-04-02 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0077_alter_conversation_token_usage_warning"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="history_length",
            field=models.PositiveBigIntegerField(
                default=15, verbose_name="Chat history length"
            ),
        ),
        migrations.AlterField(
            model_name="conversation",
            name="is_full_memory",
            field=models.BooleanField(default=False, verbose_name="Is full memory"),
        ),
    ]
