# Generated by Django 4.1.7 on 2023-03-04 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0052_remove_userplan_original_transaction_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userplan",
            name="original_transaction_id",
            field=models.CharField(
                max_length=255, null=True, verbose_name="Original transaction id"
            ),
        ),
    ]
