from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _


class Setting(models.Model):
    label = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("Label")
    )
    key = models.CharField(
        max_length=255, blank=False, null=True, unique=True, verbose_name=_("Key")
    )
    value = models.TextField(blank=False, null=True, verbose_name=_("Value"))
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name_plural = _("Settings")
        verbose_name = _("Setting")

    def __str__(self):
        return self.label if self.label else str(self.id)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ["label", "key"]

    save_on_top = True
    date_hierarchy = "created"
    search_fields = ("id", "label", "key", "value")
    list_display_links = ("label",)
    list_display = ("id", "label", "key", "value", "created")
