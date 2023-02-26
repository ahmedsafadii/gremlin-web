# Generated by Django 4.1.7 on 2023-02-26 07:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0028_alter_usertransactions_is_credit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usertransactions",
            name="amount",
            field=models.IntegerField(default=0, null=True, verbose_name="Amount"),
        ),
        migrations.AlterField(
            model_name="usertransactions",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
    ]
