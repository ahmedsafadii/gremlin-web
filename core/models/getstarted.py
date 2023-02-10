from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class GetStartedBot(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="bot",
        blank=True,
        null=True,
        verbose_name=_("User"),
    )
    answers = models.ManyToManyField(
        "GetStartedAnswer",
        related_name="answers",
        blank=False,
        verbose_name=_("Get Started Answers"),
    )
    is_complete = models.BooleanField(
        blank=False, null=False, default=False, verbose_name=_("Is complete")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Get Started Bot")
        verbose_name_plural = _("Get Started Bots")

    def __str__(self):
        return self.user.username


class GetStartedQuestion(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    question = models.TextField(
        max_length=255, blank=False, null=True, verbose_name=_("Device id")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Get Started Question")
        verbose_name_plural = _("Get Started Questions")
        ordering = ["order"]

    def __str__(self):
        return self.question


class GetStartedAnswer(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    question = models.ForeignKey(
        GetStartedQuestion,
        related_name="answers",
        on_delete=models.RESTRICT,
        null=False,
        blank=False,
        verbose_name=_("Question"),
    )
    answer = models.TextField(null=False, blank=False, verbose_name=_("Answer"))
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Get Started Answer")
        verbose_name_plural = _("Get Started Answers")
        ordering = ["order"]

    def __str__(self):
        return self.question


@admin.register(GetStartedBot)
class GetStartedBotAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user",)
    filter_horizontal = ["answers"]
    search_fields = ["user__username"]
    list_display = ["id", "user", "is_complete", "created"]
    list_filter = ["is_complete"]


@admin.register(GetStartedQuestion)
class GetStartedQuestionAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ["question"]
    list_display = ["id", "question", "created"]


@admin.register(GetStartedAnswer)
class GetStartedAnswerAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ["question"]
    list_display = ["id", "question", "created"]
