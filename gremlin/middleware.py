import sentry_sdk
from django.http import JsonResponse
from django.utils import translation
from rest_framework import pagination
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_401_UNAUTHORIZED,
)
from django.utils.translation import gettext_lazy as _
from rest_framework.views import exception_handler

from gremlin.entity import get_field
from gremlin.settings_dev import DEBUG, IOS_KEY

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class CheckKeyMiddleware(MiddlewareMixin):
    def process_request(self, request):  # noqa
        if "/v1/" in request.META["PATH_INFO"]:
            if "HTTP_GREMLIN_KEY" in request.META:
                key = request.META["HTTP_GREMLIN_KEY"]
                if key not in [IOS_KEY]:
                    return response(
                        False,
                        None,
                        _("Wrong Gremlin Key"),
                        code=HTTP_401_UNAUTHORIZED,
                    )
            else:
                return response(
                    False,
                    None,
                    _("Missing Gremlin Key"),
                    code=HTTP_401_UNAUTHORIZED,
                )


class ForceDefaultLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language_code = request.LANGUAGE_CODE
        translation.activate(language_code)
        response_object = self.get_response(request)
        translation.deactivate()
        return response_object


def generic_error_fix(errors):
    error = "Unable to detect the error"
    print(errors)
    for key, error in errors.items():
        error = get_field(key=key, error=error)
    return error


def response(status=True, data=None, message=None, code=None):
    if isinstance(message, dict):
        message = generic_error_fix(message)

    data = {
        "status": status,
        "data": data,
        "message": str(message).capitalize() if message else "",
    }

    return JsonResponse(
        data=data,
        status=(HTTP_200_OK if status else HTTP_400_BAD_REQUEST)
        if code is None
        else code,
    )


def custom_exception_handler(exc, context):
    response_context = exception_handler(exc, context)
    return response(False, None, exc.detail, code=response_context.status_code)


def catch_custom_exception(exception, request=None):
    guest = 0
    with sentry_sdk.push_scope() as scope:
        if request is not None:
            if request.user is not None:
                if request.user.is_authenticated:
                    guest = request.user.id
                    scope.set_user({"userId": request.user.id})
        scope.set_extra("userId", guest)
    sentry_sdk.capture_exception(exception)


class CustomMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):  # noqa
        if DEBUG:
            raise exception
        catch_custom_exception(exception, request)
        return response(
            False,
            None,
            _("an unexpected error happened which might be temporary"),
            code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        data = {
            "next": True if self.get_next_link() else False,
            "results": data,
        }

        return response(True, data)
