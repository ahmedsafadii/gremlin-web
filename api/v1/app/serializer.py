from rest_framework import serializers
from core.models import Plan, OnBoarding


class OnBoardingSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = OnBoarding
        fields = ["id", "title", "image"]


class PlanSerializer(serializers.ModelSerializer):  # noqa
    wordsAmount = serializers.ReadOnlyField(source="words_amount")
    maxRequestPerHour = serializers.ReadOnlyField(source="max_request_per_hour")
    bundleId = serializers.ReadOnlyField(source="bundle_id")

    class Meta:
        model = Plan
        fields = ["id", "title", "wordsAmount", "maxRequestPerHour", "bundleId"]


class ToolsSerializer(serializers.Serializer):  # noqa
    def to_representation(self, instance):
        context = self.context
        data = {
            "plans": PlanSerializer(context.get("plans"), many=True).data,
            "onBoarding": OnBoardingSerializer(
                context.get("onBoarding"), many=True
            ).data,
        }

        return data
