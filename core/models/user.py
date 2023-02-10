from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Device(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="devices",
        blank=True,
        null=True,
        verbose_name=_("User"),
    )
    device_id = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("Device id")
    )
    platform = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Platform")
    )
    language = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Language")
    )
    sessions = models.IntegerField(
        blank=True, default=0, null=True, verbose_name=_("Sessions")
    )
    app_version = models.CharField(
        blank=True, default="", max_length=255, null=True, verbose_name=_("App version")
    )
    app_build = models.CharField(
        blank=True, default="", max_length=255, null=True, verbose_name=_("App build")
    )
    first_session = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, verbose_name=_("First Session")
    )
    last_active = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name=_("Last active")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")

    def __str__(self):
        return self.device_id


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    search_fields = ["device_id"]
    list_display = [
        "id",
        "user",
        "device_id",
        "sessions",
        "app_version",
        "app_build",
        "first_session",
        "last_active",
    ]
    readonly_fields = ["sessions"]
    list_filter = ["app_version", "platform"]


class UserPlan(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="plans",
        blank=True,
        null=True,
        db_index=True,
        verbose_name=_("User"),
    )
    plan = models.ForeignKey(
        "Plan",
        on_delete=models.CASCADE,
        related_name="plan",
        blank=True,
        db_index=True,
        null=True,
        verbose_name=_("Plan"),
    )
    apple_transaction_id = models.BigIntegerField(
        blank=False,
        null=True,
        verbose_name=_("Apple Transaction id"),
    )
    expire_in = models.DateTimeField(
        blank=False, null=True, verbose_name=_("Expire in")
    )
    is_active = models.BooleanField(
        blank=False,
        db_index=True,
        default=False,
        null=False,
        verbose_name=_("Is active"),
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, db_index=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("User Plan")
        verbose_name_plural = _("Users Plans")

    def __str__(self):
        return "%s %s" % (self.user.username, self.plan.title)


@admin.register(UserPlan)
class UserPlanAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user", "plan")
    search_fields = ["user__email"]
    list_display = [
        "id",
        "user",
        "plan",
        "expire_in",
        "is_active",
        "created",
        "updated",
    ]
    list_filter = ["plan"]
