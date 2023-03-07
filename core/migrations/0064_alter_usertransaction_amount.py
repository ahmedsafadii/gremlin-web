# Generated by Django 4.1.7 on 2023-03-05 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0063_alter_conversation_history_length_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usertransaction",
            name="amount",
            field=models.PositiveBigIntegerField(
                default=0, null=True, verbose_name="Amount"
            ),
        ),
    ]