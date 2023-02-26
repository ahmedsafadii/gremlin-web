from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from api.v1.app.serializer import ToolsSerializer
from core.models import Plan, OnBoarding, Topic
from gremlin.middleware import response


class Tools(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def _get_on_boarding_and_plans():
        plans_qs = (
            Plan.objects.filter(is_active=True)
            .only("id", "title", "tokens", "max_request_per_hour", "bundle_id")
            .order_by("order")
        )
        on_boarding_qs = OnBoarding.objects.only("id", "title", "image")
        topics_qs = Topic.objects.only("id", "title")
        return on_boarding_qs, plans_qs, topics_qs

    def get(self, request):  # noqa
        onBoarding, plans, topics = self._get_on_boarding_and_plans()
        context = {
            "request": request,
            "plans": plans,
            "onBoarding": onBoarding,
            "topics": topics,
        }
        tools_ser = ToolsSerializer(data=request.data, context=context)
        if tools_ser.is_valid():
            return response(True, tools_ser.data)
        else:
            return response(False, None, tools_ser.errors)
