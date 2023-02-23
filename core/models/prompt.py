from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _


class Topic(models.Model):
    title = models.CharField(
        max_length=255, blank=False, null=False, default="", verbose_name=_("Title")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    def __str__(self):
        return self.title


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = [
        "id",
        "title",
        "created",
        "updated",
    ]


class SubTopic(models.Model):
    topic = models.ForeignKey(
        Topic,
        related_name="subtopics",
        on_delete=models.RESTRICT,
        verbose_name=_("Topic"),
        null=True,
        blank=False,
    )
    title = models.CharField(
        max_length=255, blank=False, null=False, default="", verbose_name=_("Title")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Sub Topic")
        verbose_name_plural = _("Sub Topics")

    def __str__(self):
        return self.title


@admin.register(SubTopic)
class SubTopicAdmin(admin.ModelAdmin):
    autocomplete_fields = ["topic"]
    search_fields = ["title"]
    list_display = [
        "id",
        "topic",
        "title",
        "created",
        "updated",
    ]


class Prompt(models.Model):
    title = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Title")
    )
    sub_topic = models.ForeignKey(
        SubTopic,
        related_name="prompts",
        on_delete=models.RESTRICT,
        verbose_name=_("Sub Topic"),
        null=True,
        blank=False,
    )
    content = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Content")
    )
    placeholder = models.TextField(
        blank=False,
        null=False,
        default="",
        verbose_name=_("Placeholder"),
    )
    hidden_prompt = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Hidden prompt")
    )
    is_active = models.BooleanField(
        blank=False, default=True, null=False, verbose_name=_("Is active")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Prompt")
        verbose_name_plural = _("Prompts")

    def __str__(self):
        return self.title


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_filter = ["sub_topic__topic"]
    autocomplete_fields = ["sub_topic"]
    search_fields = ["title", "content"]
    list_display = [
        "id",
        "title",
        "placeholder",
        "created",
        "updated",
    ]
