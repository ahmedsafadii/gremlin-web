from rest_framework import serializers
from api.v1.app.serializer import SubTopicSerializer
from api.v1.user.serializer import UserSerializer
from core.models import (
    GetStartedQuestion,
    GetStartedAnswer,
    GetStartedBot,
    Device,
    Prompt,
    Message,
    Conversation,
)
from django.utils.translation import gettext_lazy as _
from utils.helper import get_setting_value
from utils.openai import OpenAIManager


class GetStartedHistorySerializer(serializers.Serializer):  # noqa
    deviceId = serializers.CharField(required=True, allow_blank=False)

    @staticmethod
    def _create_question_dict(question, nickname="", is_rendered=True):
        return {
            "questionId": question.id,
            "message": question.question.replace("{username}", nickname),
            "isRendered": is_rendered,
            "isGremlin": True,
        }

    @staticmethod
    def _create_answer_dict(answer):
        return {
            "answerId": answer.id,
            "message": answer.answer,
            "isRendered": True,
            "isGremlin": False,
        }

    def _get_started_history(self, device_id):
        first_question = GetStartedQuestion.objects.get(order=1)
        device_bot, device_created = GetStartedBot.objects.update_or_create(
            device__device_id=device_id
        )
        first_question_dict = self._create_question_dict(
            first_question, is_rendered=False
        )
        history = []

        try:
            if device_bot.answers.count() > 0:
                next_question = 1
                for answer in device_bot.answers.all().order_by("id"):
                    next_question = answer.question.order
                    history.append(
                        self._create_question_dict(
                            answer.question, nickname=device_bot.nickname
                        )
                    )
                    history.append(self._create_answer_dict(answer))
                next_question = GetStartedQuestion.objects.filter(
                    order=next_question + 1
                )
                if next_question.exists():
                    next_question = next_question.first()
                    device_bot.is_complete = next_question.is_final_question
                    history.append(
                        self._create_question_dict(
                            next_question, nickname=device_bot.nickname
                        )
                    )
                else:
                    device_bot.is_complete = True
                device_bot.save()
            else:
                history.append(first_question_dict)
        except GetStartedBot.DoesNotExist:
            device, device_created = Device.objects.get_or_create(device_id=device_id)
            GetStartedBot.objects.update_or_create(device=device)
            history.append(first_question_dict)

        return {"messages": history, "isCompleted": device_bot.is_complete}

    def save(self, **kwargs):
        validated_data = self.validated_data
        device_id = validated_data.get("deviceId")
        return self._get_started_history(device_id=device_id)


class GetStartedSerializer(serializers.Serializer):  # noqa
    questionId = serializers.CharField(required=True, allow_blank=False)
    answer = serializers.CharField(required=True, allow_blank=False)
    deviceId = serializers.CharField(required=True, allow_blank=False)

    @staticmethod
    def _create_question_dict(question, nickname="", is_rendered=True):
        return {
            "questionId": question.id,
            "message": question.question.replace("{username}", nickname),
            "isRendered": is_rendered,
            "isGremlin": True,
        }

    def _store_answer_and_give_next_question(self, device_id, question_id, answer):
        device, device_created = Device.objects.get_or_create(device_id=device_id)
        device_bot, device_bot_created = GetStartedBot.objects.update_or_create(
            device=device
        )
        answer_object, answer_created = GetStartedAnswer.objects.update_or_create(
            question_id=question_id, bot=device_bot
        )

        if answer_created:
            answer_object.answer = answer
            answer_object.save()
            if answer_object.question.order == 1:
                device_bot.nickname = answer
                device_bot.save()
        try:
            question = GetStartedQuestion.objects.get(id=question_id)
            next_question = GetStartedQuestion.objects.filter(order=question.order + 1)
            if next_question.exists():
                next_question = next_question.first()
                device_bot.is_complete = next_question.is_final_question
            else:
                device_bot.is_complete = True
            device_bot.save()

            message = self._create_question_dict(
                question=next_question, nickname=device_bot.nickname, is_rendered=False
            )
            return {"messages": [message], "isCompleted": device_bot.is_complete}
        except (Exception,):
            raise serializers.ValidationError(
                {"general": [_("Unable to get the next question")]}
            )

    def save(self, **kwargs):
        validated_data = self.validated_data
        device_id = validated_data.get("deviceId")
        question_id = validated_data.get("questionId")
        answer = validated_data.get("answer")
        return self._store_answer_and_give_next_question(
            device_id=device_id, question_id=question_id, answer=answer
        )


class PromptsSerializer(serializers.ModelSerializer):
    topic = SubTopicSerializer(many=False, source="sub_topic")

    class Meta:
        model = Prompt
        fields = ["id", "topic", "title", "content", "placeholder"]


class PublicLobbySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    @staticmethod
    def get_user(obj):
        user = UserSerializer(obj.conversation.user, many=False).data
        return {"nickName": user["nickName"], "color": user["userColor"]}

    class Meta:
        model = Message
        fields = ["id", "question", "answer", "user"]


class MessageSerializer(serializers.ModelSerializer):
    conversationId = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    @staticmethod
    def get_balance(obj):
        return (
            UserSerializer(obj.conversation.user)
            .data.get("balance", {})
            .get("balance", 0)
        )

    @staticmethod
    def get_conversationId(obj):
        return obj.conversation.id

    class Meta:
        model = Message
        fields = ["id", "question", "answer", "conversationId", "balance"]


class ConversationSerializer(serializers.ModelSerializer):
    prompt = PromptsSerializer(many=False)
    historyLength = serializers.ReadOnlyField(source="history_length")
    showInPublicLobby = serializers.ReadOnlyField(source="show_in_public_lobby")
    tokenUsageWarning = serializers.ReadOnlyField(source="token_usage_warning")
    isCustomTitle = serializers.ReadOnlyField(source="is_custom_title")
    tokenMaxUsage = serializers.SerializerMethodField()
    totalMessages = serializers.SerializerMethodField()

    @staticmethod
    def get_totalMessages(obj):
        return obj.messages.count()

    @staticmethod
    def get_tokenMaxUsage():
        return 4000

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "prompt",
            "showInPublicLobby",
            "historyLength",
            "tokenUsageWarning",
            "isCustomTitle",
            "tokenMaxUsage",
            "totalMessages",
            "created",
        ]


class CreateMessageSerializer(serializers.Serializer):  # noqa
    prompt = serializers.CharField(required=True, allow_null=False)
    wizardId = serializers.CharField(required=False, allow_null=False)
    conversationId = serializers.CharField(required=False, allow_null=False)

    def validate_conversationId(self, value):
        try:
            user = self.context.get("request").user
            return Conversation.objects.get(id=value, is_deleted=False, user=user)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError(_("This Conversation is not available"))

    @staticmethod
    def validate_wizardId(value):
        try:
            return Prompt.objects.get(id=value, is_active=True)
        except Prompt.DoesNotExist:
            raise serializers.ValidationError(_("This prompt is not available"))

    def validate(self, attrs):
        # Check user balance
        user = self.context.get("request").user
        user_balance = UserSerializer(user).data.get("balance", {}).get("balance", 0)
        if user_balance <= 0:
            raise serializers.ValidationError(_("You are out of balance"))

        return attrs

    @staticmethod
    def send_prompt_request(prompt):
        open_ai_manager = OpenAIManager(is_general_chat=True)
        return open_ai_manager.create_completion(prompt=prompt)

    def _save_general_chat_result(self, prompt, hidden_prompt, conversation, result):
        user = self.context.get("request").user
        text = result["choices"][0]["text"].strip().rstrip("\n ,")
        title = text[:30].replace("\n", " ")
        hidden_prompt += text + "\n Human: "
        usage = result["usage"]
        prompt_tokens_usage = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]
        total_tokens = usage["total_tokens"]

        if conversation:
            conversation.title = title
            conversation.save()
        else:
            conversation = Conversation.objects.create(
                user=user,
                title=title,
                history_length=0,
            )

        message = self.create_message(
            conversation=conversation,
            question=prompt,
            answer=text.replace("AI: ", ""),
            prompt_tokens_usage=prompt_tokens_usage,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            hidden_prompt=hidden_prompt,
        )

        return message

    def _save_wizard_result(self, prompt, wizard, conversation, result, hidden_prompt):
        user = self.context.get("request").user
        text = result["choices"][0]["text"].strip().rstrip("\n ,")
        title = text[:30].replace("\n", " ")
        hidden_prompt += text + "\n Human: "
        usage = result["usage"]
        prompt_tokens_usage = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]
        total_tokens = usage["total_tokens"]

        if conversation:
            conversation.title = title
            conversation.save()
        else:
            conversation = Conversation.objects.create(
                user=user,
                title=title,
                prompt=wizard,
                history_length=0,
            )

        message = self.create_message(
            conversation=conversation,
            question=prompt,
            answer=text.replace("AI: ", ""),
            prompt_tokens_usage=prompt_tokens_usage,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            hidden_prompt=hidden_prompt,
        )

        return message

    @staticmethod
    def create_message(
        conversation,
        question,
        answer,
        prompt_tokens_usage,
        completion_tokens,
        total_tokens,
        hidden_prompt,
    ):
        message = Message.objects.create(
            conversation=conversation,
            question=question,
            answer=answer,
            prompt_tokens_usage=prompt_tokens_usage,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            hidden_prompt=hidden_prompt,
        )
        return message

    def create(self, validated_data):
        wizard = self.validated_data.get("wizardId", None)
        prompt = self.validated_data.get("prompt", None)
        conversation = self.validated_data.get("conversationId", None)
        user = self.context.get("request").user

        nickname = (
            UserSerializer().get_nickName(user, is_shortcut=False)
            if UserSerializer().get_nickName(user, is_shortcut=False)
            else "Gremlin"
        )

        if wizard:
            if conversation:
                messages = Message.objects.filter(
                    conversation=conversation, conversation__user=user
                ).latest("id")
                hidden_prompt = messages.hidden_prompt + " " + prompt + "\n AI:"
            else:
                wizard_prompt = wizard.hidden_prompt.replace(
                    "[PROMPT]", prompt
                ).replace("[TARGETLANGUAGE]", "English")
                hidden_prompt = (
                    get_setting_value(key="wizard_chat_prompt")
                    .replace("[NICKNAME]", f"({nickname}")
                    .replace("[WIZARD]", wizard.sub_topic.title)
                )
                hidden_prompt += " " + wizard_prompt + "\n AI: "

            response_status, response_data = self.send_prompt_request(
                prompt=hidden_prompt
            )
            message = self._save_wizard_result(
                prompt=prompt,
                wizard=wizard,
                hidden_prompt=hidden_prompt,
                conversation=conversation,
                result=response_data,
            )
        else:
            if conversation:
                messages = Message.objects.filter(
                    conversation=conversation, conversation__user=user
                ).latest("id")
                hidden_prompt = messages.hidden_prompt + " " + prompt + "\n AI:"
            else:
                hidden_prompt = get_setting_value(key="general_chat_prompt").replace(
                    "[NICKNAME]", f"({nickname}"
                )
                hidden_prompt += " " + prompt + "\n AI: "
            response_status, response_data = self.send_prompt_request(
                prompt=hidden_prompt
            )
            message = self._save_general_chat_result(
                prompt=prompt,
                hidden_prompt=hidden_prompt,
                conversation=conversation,
                result=response_data,
            )

        if not response_status:
            raise serializers.ValidationError(response_data)

        return [MessageSerializer(message, many=False).data]
