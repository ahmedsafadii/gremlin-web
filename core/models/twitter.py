from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class TwitterAccount(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="twitter",
        blank=True,
        null=True,
        db_index=True,
        verbose_name=_("User"),
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Twitter Account")
        verbose_name_plural = _("Twitters Accounts")

    def __str__(self):
        return self.user.username


class TwitterAI(models.Model):
    twitter_account = models.ForeignKey(
        TwitterAccount,
        on_delete=models.RESTRICT,
        related_name="ai",
        blank=False,
        null=True,
        verbose_name=_("Twitter Account"),
    )
    message = models.ForeignKey(
        "Message",
        on_delete=models.RESTRICT,
        related_name="messages",
        blank=False,
        null=True,
        verbose_name=_("Prompt"),
    )
    schedule_date = models.DateTimeField(
        blank=False, null=False, verbose_name=_("Schedule Date")
    )
    is_tweeted = models.BooleanField(
        default=False, null=False, blank=False, verbose_name=_("Is tweeted")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Twitter AI")
        verbose_name_plural = _("Twitters AIS")

    def __str__(self):
        return self.message.answer


@admin.register(TwitterAccount)
class TwitterAccountAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    list_display = [
        "id",
        "user",
        "created",
        "updated",
    ]


@admin.register(TwitterAI)
class TwitterAIAdmin(admin.ModelAdmin):
    search_fields = ["message__answer", "twitter_account__user__username"]
    list_display = [
        "id",
        "twitter_account",
        "message",
        "schedule_date",
        "is_tweeted",
        "created",
        "updated",
    ]
