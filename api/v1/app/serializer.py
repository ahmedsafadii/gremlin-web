from rest_framework import serializers
from core.models import Plan, OnBoarding, Topic
from utils.helper import get_setting_value


class OnBoardingSerializer(serializers.ModelSerializer):  # noqa
    subTitle = serializers.ReadOnlyField(source="sub_title")

    class Meta:
        model = OnBoarding
        fields = ["id", "title", "subTitle", "image"]


class PlanSerializer(serializers.ModelSerializer):  # noqa
    bundleId = serializers.ReadOnlyField(source="bundle_id")
    isSubscription = serializers.ReadOnlyField(source="is_subscription")
    promotionText = serializers.ReadOnlyField(source="promotion_text")
    subTitle = serializers.ReadOnlyField(source="sub_title")

    class Meta:
        model = Plan
        fields = [
            "id",
            "title",
            "order",
            "tokens",
            "subTitle",
            "bundleId",
            "isSubscription",
            "promotionText",
        ]


class ToolsSerializer(serializers.Serializer):  # noqa
    def to_representation(self, instance):
        context = self.context
        data = {
            "plans": {
                "subscription": PlanSerializer(
                    context.get("subscription"), many=True
                ).data,
                "asYouGo": PlanSerializer(context.get("asYouGo"), many=True).data,
            },
            "onBoarding": OnBoardingSerializer(
                context.get("onBoarding"), many=True
            ).data,
            "topics": TopicSerializer(context.get("topics"), many=True).data,
            "settings": {
                "privacyPolicy": str(get_setting_value("privacy_policy")),
                "termsOfService": str(get_setting_value("terms_of_service")),
            },
        }

        return data


class TopicSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Topic
        fields = ["id", "title"]
