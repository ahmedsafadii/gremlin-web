# Generated by Django 4.1.7 on 2023-02-28 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0035_plan_is_free_trail"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="plan",
            name="is_free_trail",
        ),
        migrations.AddField(
            model_name="plan",
            name="is_free_trial",
            field=models.BooleanField(default=False, verbose_name="Is subscription"),
        ),
    ]