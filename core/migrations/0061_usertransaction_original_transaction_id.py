# Generated by Django 4.1.7 on 2023-03-05 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0060_alter_applewebhook_notification_subtype"),
    ]

    operations = [
        migrations.AddField(
            model_name="usertransaction",
            name="original_transaction_id",
            field=models.CharField(
                max_length=255, null=True, verbose_name="Original transaction id"
            ),
        ),
    ]
