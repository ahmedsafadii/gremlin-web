# Generated by Django 4.1.7 on 2023-02-28 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0033_alter_conversation_show_in_public_lobby"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="is_subscription",
            field=models.BooleanField(default=False, verbose_name="Is subscription"),
        ),
    ]
