# Generated by Django 4.1.5 on 2023-02-11 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_remove_plan_max_request_plan_max_request_per_hour_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="getstartedquestion",
            name="question",
            field=models.TextField(max_length=255, null=True, verbose_name="Question"),
        ),
    ]