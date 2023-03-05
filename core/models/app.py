from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.helper import RandomFileName


class AppleWebHook(models.Model):
    get_body = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Get Body")
    )
    post_body = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Post Body")
    )
    error = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Error")
    )
    is_processed = models.BooleanField(
        default=False, null=False, blank=False, verbose_name=_("Is processed")
    )
    json_processed = models.TextField(
        blank=False, null=False, default="", verbose_name=_("Error")
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("Apple Web Hook")
        verbose_name_plural = _("Apple Web Hook")

    def __str__(self):
        return str(self.id)


@admin.register(AppleWebHook)
class AppleWebHookAdmin(admin.ModelAdmin):
    search_fields = ["id", "get_body", "post_body", "error"]
    list_display = [
        "id",
        "get_body",
        "is_processed",
        "created",
        "updated",
    ]


class OnBoarding(models.Model):
    title = models.CharField(
        max_length=255, blank=False, null=False, default="", verbose_name=_("Title")
    )
    image = models.FileField(
        upload_to=RandomFileName("on_boarding"),
        blank=False,
        null=False,
        default="",
        verbose_name=_("Image"),
    )
    created = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name=_("Created")
    )
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name=_("Updated"))

    class Meta:
        verbose_name = _("On Boarding")
        verbose_name_plural = _("On Boardings")

    def __str__(self):
        return self.title


@admin.register(OnBoarding)
class OnBoardingAdmin(admin.ModelAdmin):
    search_fields = ["title", "image"]
    list_display = [
        "id",
        "title",
        "image",
        "created",
        "updated",
    ]
