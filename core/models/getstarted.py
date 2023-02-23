from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _


class GetStartedBot(models.Model):
    device = models.ForeignKey(
        "Device",
        on_delete=models.CASCADE,
        related_name="bot",
        blank=True,
        null=True,
        verbose_name=_("Device"),
    )
    nickname = models.CharField(
        max_length=255, null=False, blank=False, default="", verbose_name=_("Nickname")
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
        return str(self.id)


class GetStartedQuestion(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    question = models.TextField(blank=False, null=True, verbose_name=_("Question"))
    is_final_question = models.BooleanField(
        default=False, null=False, blank=False, verbose_name=_("Is final question")
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
    bot = models.ForeignKey(
        "GetStartedBot",
        on_delete=models.CASCADE,
        related_name="answers",
        blank=True,
        null=True,
        verbose_name=_("Device"),
    )
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
        return str(self.id)


@admin.register(GetStartedBot)
class GetStartedBotAdmin(admin.ModelAdmin):
    autocomplete_fields = ("device",)
    search_fields = ["device__device_id"]
    list_display = ["id", "device", "nickname", "is_complete", "created"]
    list_filter = ["is_complete"]


@admin.register(GetStartedQuestion)
class GetStartedQuestionAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ["question"]
    list_display = ["id", "question", "is_final_question", "created"]


@admin.register(GetStartedAnswer)
class GetStartedAnswerAdmin(SortableAdminMixin, admin.ModelAdmin):
    autocomplete_fields = ["bot"]
    search_fields = ["question"]
    list_display = ["id", "bot", "answer", "created"]
