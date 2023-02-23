# Generated by Django 4.1.5 on 2023-02-15 16:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_alter_prompt_placeholder"),
    ]

    operations = [
        migrations.AlterField(
            model_name="getstartedanswer",
            name="bot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="answers",
                to="core.getstartedbot",
                verbose_name="Device",
            ),
        ),
        migrations.AlterField(
            model_name="getstartedbot",
            name="device",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bot",
                to="core.device",
                verbose_name="Device",
            ),
        ),
    ]
