# Generated by Django 4.1.5 on 2023-02-18 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_alter_conversation_prompt"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="hidden_prompt",
            field=models.TextField(null=True, verbose_name="hidden_prompt"),
        ),
    ]
