import json

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from api.v1.app.serializer import ToolsSerializer
from core.cron import check_apple_webhook
from core.models import Plan, OnBoarding, Topic
from core.models.app import AppleWebHook
from gremlin.middleware import response, catch_custom_exception


class Tools(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def _get_on_boarding_and_plans():
        subscription_qs = (
            Plan.objects.filter(is_active=True, is_subscription=True)
            .only("id")
            .order_by("order")
        )
        as_you_go_qs = (
            Plan.objects.filter(is_active=True, is_subscription=False)
            .only("id")
            .order_by("order")
        )
        on_boarding_qs = OnBoarding.objects.only("id", "title", "image")
        topics_qs = Topic.objects.only("id", "title").order_by("-order")
        return on_boarding_qs, subscription_qs, topics_qs, as_you_go_qs

    def get(self, request):  # noqa
        onBoarding, subscription, topics, as_you_go = self._get_on_boarding_and_plans()
        context = {
            "request": request,
            "subscription": subscription,
            "asYouGo": as_you_go,
            "onBoarding": onBoarding,
            "topics": topics,
        }
        tools_ser = ToolsSerializer(data=request.data, context=context)
        if tools_ser.is_valid():
            return response(True, tools_ser.data)
        else:
            return response(False, None, tools_ser.errors)


class AppleWebHookView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):  # noqa
        try:
            get_body = dict(request.GET.items())
            post_body = request.data if request.data else {}
            hook = AppleWebHook()
            hook.is_processed = False
            hook.get_body = json.dumps(get_body)
            hook.post_body = json.dumps(post_body)
            hook.save()
            check_apple_webhook(hook_id=hook.id)
            return response(True, "Response saved")
        except Exception as e:
            hook = AppleWebHook()
            hook.error = str(e)
            hook.is_processed = False
            hook.save()
            catch_custom_exception(e, request)
            return response(False, str(e))
