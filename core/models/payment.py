from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from adminsortable2.admin import SortableAdminMixin


class Plan(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    title = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("Title")
    )
    sub_title = models.TextField(blank=False, null=True, verbose_name=_("Subtitle"))
    tokens = models.PositiveBigIntegerField(
        blank=False, null=True, verbose_name=_("Tokens")
    )
    max_request_per_hour = models.IntegerField(
        blank=False, null=True, verbose_name=_("Max request per hour")
    )
    bundle_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Bundle id")
    )
    is_active = models.BooleanField(
        blank=False, null=False, default=False, verbose_name=_("Is active")
    )
    is_subscription = models.BooleanField(
        blank=False, null=False, default=False, verbose_name=_("Is subscription")
    )
    promotion_text = models.TextField(
        blank=True,
        null=False,
        default="",
        verbose_name=_("Promotion text"),
        help_text=_("Use {{amount}} for amount"),
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")
        ordering = ["order"]

    def __str__(self):
        return self.title


@admin.register(Plan)
class PlanAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ["title"]
    list_display = [
        "id",
        "title",
        "tokens",
        "max_request_per_hour",
        "bundle_id",
        "is_active",
        "created",
        "updated",
    ]
