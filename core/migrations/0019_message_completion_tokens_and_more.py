# Generated by Django 4.1.5 on 2023-02-18 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_message_hidden_prompt"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="completion_tokens",
            field=models.IntegerField(
                null=True, verbose_name="Completion tokens usage"
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="prompt_tokens_usage",
            field=models.IntegerField(null=True, verbose_name="Prompt tokens usage"),
        ),
        migrations.AddField(
            model_name="message",
            name="total_tokens",
            field=models.IntegerField(null=True, verbose_name="Total token usage"),
        ),
    ]
