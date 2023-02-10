from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="conversations",
        blank=True,
        null=True,
        verbose_name=_("User"),
    )
    title = models.CharField(
        max_length=255, blank=False, default="", verbose_name=_("Title")
    )
    is_deleted = models.BooleanField(
        default=False, blank=False, verbose_name=_("Is deleted")
    )
    history_length = models.IntegerField(
        default=0, blank=False, null=False, verbose_name=_("Chat history length")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return self.title


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    search_fields = ["user__username", "title"]
    autocomplete_fields = ["user"]
    list_display = [
        "id",
        "user",
        "title",
        "is_deleted",
        "history_length",
        "created",
        "updated",
    ]


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.RESTRICT,
        related_name="messages",
        blank=False,
        null=True,
        verbose_name=_("Conversation"),
    )
    prompt = models.ForeignKey(
        "Prompt",
        on_delete=models.RESTRICT,
        related_name="messages",
        blank=False,
        null=True,
        verbose_name=_("Prompt"),
    )
    question = models.TextField(blank=False, null=True, verbose_name=_("Question"))
    answer = models.TextField(blank=True, null=True, verbose_name=_("Answer"))
    token_cost = models.IntegerField(blank=False, verbose_name=_("Token cost"))
    is_deleted = models.BooleanField(
        default=False, blank=False, verbose_name=_("Is deleted")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return self.conversation.title

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        from core.models import TwitterAI

        try:
            old_instance = TwitterAI.objects.get(pk=self.pk)
        except TwitterAI.DoesNotExist:
            old_instance = None

        if (
            old_instance
            and old_instance.is_deleted != self.is_deleted
            and self.is_deleted
        ):
            TwitterAI.objects.filter(message_id=self.id).delete()

        super().save(force_insert, force_update, using, update_fields)
