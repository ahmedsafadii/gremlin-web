from rest_framework import serializers
from core.models import Plan, OnBoarding, SubTopic, Topic


class OnBoardingSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = OnBoarding
        fields = ["id", "title", "image"]


class PlanSerializer(serializers.ModelSerializer):  # noqa
    maxRequestPerHour = serializers.ReadOnlyField(source="max_request_per_hour")
    bundleId = serializers.ReadOnlyField(source="bundle_id")

    class Meta:
        model = Plan
        fields = ["id", "title", "tokens", "maxRequestPerHour", "bundleId"]


class ToolsSerializer(serializers.Serializer):  # noqa
    def to_representation(self, instance):
        context = self.context
        data = {
            "plans": PlanSerializer(context.get("plans"), many=True).data,
            "onBoarding": OnBoardingSerializer(
                context.get("onBoarding"), many=True
            ).data,
            "topics": TopicSerializer(context.get("topics"), many=True).data,
        }

        return data


class TopicSerializer(serializers.ModelSerializer):  # noqa
    class Meta:
        model = Topic
        fields = ["id", "title"]


class SubTopicSerializer(serializers.ModelSerializer):  # noqa
    category = TopicSerializer(many=False, source="topic")

    class Meta:
        model = SubTopic
        fields = ["id", "title", "category"]
