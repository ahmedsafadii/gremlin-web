# Generated by Django 4.1.7 on 2023-03-04 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0054_applewebhook_is_processed"),
    ]

    operations = [
        migrations.AddField(
            model_name="applewebhook",
            name="json_processed",
            field=models.TextField(default="", verbose_name="Error"),
        ),
    ]
