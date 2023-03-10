# Generated by Django 4.1.7 on 2023-03-09 19:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0066_alter_prompt_sub_topic_alter_subtopic_topic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="conversation",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="core.conversation",
                verbose_name="Conversation",
            ),
        ),
    ]
