# Generated by Django 4.1.7 on 2023-02-26 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_alter_usertransactions_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usertransactions",
            name="is_credit",
            field=models.BooleanField(default=0, verbose_name="Is credit"),
        ),
    ]