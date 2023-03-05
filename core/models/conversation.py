from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from api.v1.user.serializer import UserSerializer
from core.models.user import UserTransaction


class Conversation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name="conversations",
        blank=True,
        null=True,
        verbose_name=_("User"),
    )
    prompt = models.ForeignKey(
        "Prompt",
        on_delete=models.RESTRICT,
        related_name="conversations",
        blank=True,
        null=True,
        verbose_name=_("Prompt"),
    )
    title = models.CharField(
        max_length=255, blank=False, default="", verbose_name=_("Title")
    )
    token_usage_warning = models.PositiveIntegerField(
        blank=False, default=200, verbose_name=_("Token usage warning")
    )
    is_custom_title = models.BooleanField(
        default=False, blank=False, verbose_name=_("Is custom title")
    )
    is_full_memory = models.BooleanField(
        default=True, blank=False, verbose_name=_("Is full memory")
    )
    is_deleted = models.BooleanField(
        default=False, blank=False, verbose_name=_("Is deleted")
    )
    history_length = models.IntegerField(
        default=1, blank=False, null=False, verbose_name=_("Chat history length")
    )
    show_in_public_lobby = models.BooleanField(
        default=False, null=False, blank=False, verbose_name=_("Is public lobby?")
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
    autocomplete_fields = ["user", "prompt"]
    list_display = [
        "id",
        "user",
        "prompt",
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
    question = models.TextField(blank=False, null=True, verbose_name=_("Question"))
    answer = models.TextField(blank=True, null=True, verbose_name=_("Answer"))
    hidden_prompt = models.TextField(
        blank=False, null=True, verbose_name=_("Hidden prompt")
    )
    prompt_tokens_usage = models.IntegerField(
        blank=False, null=True, verbose_name=_("Prompt tokens usage")
    )
    completion_tokens = models.IntegerField(
        blank=False, null=True, verbose_name=_("Completion tokens usage")
    )
    total_tokens = models.IntegerField(
        blank=False, null=True, verbose_name=_("Total token usage")
    )
    is_deleted = models.BooleanField(
        default=False, blank=False, verbose_name=_("Is deleted")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self):
        return self.conversation.title


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    search_fields = ["conversation__title"]
    autocomplete_fields = ["conversation"]
    list_display = [
        "id",
        "conversation",
        "question",
        "answer",
        "prompt_tokens_usage",
        "completion_tokens",
        "total_tokens",
        "is_deleted",
        "created",
    ]
    list_editable = ["is_deleted"]


@receiver(post_save, sender=Message)
def my_post_save_function(sender, instance, created, **kwargs):
    """
    A post save signal function for the Message model.
    """
    if created:
        total_tokens = instance.total_tokens
        user_balance = (
            UserSerializer(instance.conversation.user)
            .data.get("balance", {})
            .get("balance", 0)
        )
        if total_tokens >= user_balance:
            total_tokens = user_balance
        UserTransaction.objects.create_transaction(
            user=instance.conversation.user,
            original_transaction_id=None,
            amount=total_tokens,
            is_credit=False,
            notes=f"Cost for message id {instance.id}",
        )
