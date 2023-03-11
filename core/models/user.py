from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.helper import get_setting_value


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
    onesignal = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("OneSignal id")
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
    original_transaction_id = models.CharField(
        max_length=255,
        blank=False,
        null=True,
        verbose_name=_("Original transaction id"),
    )
    expire_in = models.DateTimeField(
        blank=False, null=True, verbose_name=_("Expire in")
    )
    type = models.CharField(
        max_length=255, blank=False, null=True, verbose_name=_("Type")
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
        return "%s" % self.user.username


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


class UserTransactionManager(models.Manager):
    def create_transaction(
        self,
        user,
        amount,
        is_credit,
        original_transaction_id,
        notes="",
        is_gift=False,
        is_free=False,
    ):
        transaction = self.create(
            user=user,
            is_free=is_free,
            is_gift=is_gift,
            amount=amount,
            is_credit=is_credit,
            notes=notes,
            original_transaction_id=original_transaction_id,
        )
        return transaction

    def create_free_transaction(self, user):
        transaction = self.create(
            user=user,
            is_free=True,
            amount=int(get_setting_value("free_users_tokens")),
            is_credit=True,
            notes="Free Tokens",
        )
        return transaction

    def create_rating_gift_transaction(self, user):
        transaction = self.create(
            user=user,
            is_gift=True,
            amount=int(get_setting_value("gift_users_tokens")),
            is_credit=True,
            notes="Gift Rating Tokens",
        )
        return transaction


class UserTransaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        blank=False,
        null=True,
        db_index=True,
        verbose_name=_("User"),
    )
    original_transaction_id = models.CharField(
        max_length=255,
        blank=False,
        null=True,
        verbose_name=_("Original transaction id"),
    )
    is_gift = models.BooleanField(
        blank=False, null=False, default=False, verbose_name=_("Is gift")
    )
    is_free = models.BooleanField(
        blank=False, null=False, default=False, verbose_name=_("Is Free")
    )
    amount = models.BigIntegerField(
        blank=False, default=0, null=True, verbose_name=_("Amount")
    )
    is_credit = models.BooleanField(
        blank=False, default=0, null=False, verbose_name=_("Is credit")
    )
    notes = models.TextField(blank=False, null=True, verbose_name=_("Notes"))
    created = models.DateTimeField(
        auto_now_add=True, null=True, db_index=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    objects = UserTransactionManager()

    class Meta:
        verbose_name = _("User Transaction")
        verbose_name_plural = _("Users Transactions")

    def __str__(self):
        return "%s" % self.user.username


@admin.register(UserTransaction)
class UserTransactionAdmin(admin.ModelAdmin):
    # def has_add_permission(self, request):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

    autocomplete_fields = ("user",)
    search_fields = ["user__email"]
    list_display = [
        "id",
        "user",
        "amount",
        "is_credit",
        "is_gift",
        "is_free",
        "notes",
        "created",
    ]
    list_filter = ["is_credit", "is_gift", "is_free"]
