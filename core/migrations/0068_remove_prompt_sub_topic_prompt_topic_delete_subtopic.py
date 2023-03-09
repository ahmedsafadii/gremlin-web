# Generated by Django 4.1.7 on 2023-03-09 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0067_alter_message_conversation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="prompt",
            name="sub_topic",
        ),
        migrations.AddField(
            model_name="prompt",
            name="topic",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="prompts",
                to="core.topic",
                verbose_name="Sub Topic",
            ),
        ),
        migrations.DeleteModel(
            name="SubTopic",
        ),
    ]