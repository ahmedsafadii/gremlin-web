# Generated by Django 4.1.7 on 2023-03-05 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0064_alter_usertransaction_amount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plan",
            name="tokens",
            field=models.PositiveBigIntegerField(null=True, verbose_name="Tokens"),
        ),
    ]
