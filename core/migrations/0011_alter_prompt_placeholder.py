# Generated by Django 4.1.5 on 2023-02-15 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_alter_prompt_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prompt",
            name="placeholder",
            field=models.TextField(default="", verbose_name="Placeholder"),
        ),
    ]