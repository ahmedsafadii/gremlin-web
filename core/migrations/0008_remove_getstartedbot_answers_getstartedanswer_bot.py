# Generated by Django 4.1.5 on 2023-02-11 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_getstartedbot_nickname"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="getstartedbot",
            name="answers",
        ),
        migrations.AddField(
            model_name="getstartedanswer",
            name="bot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="answers",
                to="core.getstartedbot",
                verbose_name="Device",
            ),
        ),
    ]