# Generated by Django 4.1.7 on 2023-02-26 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_usertransactions"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="usertransactions",
            options={
                "verbose_name": "User Transaction",
                "verbose_name_plural": "Users Transactions",
            },
        ),
    ]