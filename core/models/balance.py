from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class BalanceSheet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="statement",
        blank=True,
        null=True,
        verbose_name=_("User"),
    )
    TYPES = [
        ("Credit", _("Credit")),
        ("Debit", _("Debit")),
    ]
    type = models.CharField(
        choices=TYPES, blank=False, max_length=10, verbose_name=_("Type")
    )
    amount = models.BigIntegerField(
        max_length=255, blank=False, null=False, default="", verbose_name=_("Amount")
    )
    notes = models.TextField(blank=False, default="", verbose_name=_("Notes"))
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Balance Sheet")
        verbose_name_plural = _("Balance Sheets")

    def __str__(self):
        return self.amount


@admin.register(BalanceSheet)
class BalanceSheetAdmin(admin.ModelAdmin):
    search_fields = ["user__username", "image"]
    autocomplete_fields = ["user"]
    list_display = [
        "id",
        "user",
        "type",
        "amount",
        "notes",
        "created",
        "updated",
    ]
