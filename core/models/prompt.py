from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _


class Topic(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    title = models.CharField(
        max_length=255, blank=False, null=False, default="", verbose_name=_("Title")
    )
    is_active = models.BooleanField(
        blank=False, default=False, null=False, verbose_name=_("Is active")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        ordering = ["order"]

    def __str__(self):
        return self.title


@admin.register(Topic)
class TopicAdmin(SortableAdminMixin, admin.ModelAdmin):
    search_fields = ["title"]
    list_filter = ["is_active"]
    list_editable = ["is_active"]
    list_display = [
        "id",
        "title",
        "is_active",
        "created",
        "updated",
    ]


class Prompt(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
    )
    title = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Title")
    )
    topic = models.ForeignKey(
        Topic,
        related_name="prompts",
        on_delete=models.CASCADE,
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
    system_prompt = models.TextField(
        blank=True, null=False, default="", verbose_name=_("System prompt")
    )
    hidden_prompt = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Hidden prompt")
    )
    is_active = models.BooleanField(
        blank=False, default=True, null=False, verbose_name=_("Is active")
    )
    is_feature = models.BooleanField(
        blank=False, default=False, null=False, verbose_name=_("Is feature")
    )
    is_pro = models.BooleanField(
        blank=False, default=False, null=False, verbose_name=_("Is pro")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Prompt")
        verbose_name_plural = _("Prompts")
        ordering = ["order"]

    def __str__(self):
        return self.title


@admin.register(Prompt)
class PromptAdmin(SortableAdminMixin, admin.ModelAdmin):
    actions = ["deactivate_selected_prompts"]

    @admin.action(description=_("Deactivate selected prompts"))
    def deactivate_selected_prompts(self, request, queryset):
        for row in queryset:
            row.is_active = False
            row.save()

    search_fields = ["title", "content"]
    autocomplete_fields = ["topic"]
    list_filter = ["topic"]
    list_editable = ["is_active"]
    list_display = [
        "id",
        "title",
        "placeholder",
        "is_active",
        "created",
        "updated",
    ]
