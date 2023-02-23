from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from api.v1.assistant.serializer import (
    GetStartedSerializer,
    GetStartedHistorySerializer,
    PromptsSerializer,
    ConversationSerializer,
    MessageSerializer,
    CreateMessageSerializer,
)
from core.models import Prompt, Conversation, Message
from gremlin.middleware import response
from django.utils.translation import gettext_lazy as _


class GetStartedView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GetStartedSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            data = serializer.save()
            return response(True, data)
        else:
            return response(False, None, serializer.errors)


class GetStartedHistoryView(APIView):
    permission_classes = [AllowAny]
    serializer_class = GetStartedHistorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            data = serializer.save()
            return response(True, data)
        else:
            return response(False, None, serializer.errors)


class PromptsListView(generics.ListCreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PromptsSerializer

    def get_queryset(self):
        query = self.request.GET
        topic = query.get("topic", None)
        q = query.get("q", None)
        prompts = Prompt.objects.all()

        if topic:
            prompts = prompts.filter(sub_topic__topic_id=topic)
        if q:
            prompts = prompts.filter(
                Q(title__icontains=q)
                | Q(title__icontains=q)
                | Q(content__icontains=q)
                | Q(content__icontains=q)
            )
        prompts = prompts.order_by("created")
        return prompts

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DeleteConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        Conversation.objects.filter(user=user).update(is_deleted=True)
        Message.objects.filter(conversation__user=user).update(is_deleted=True)
        return response(True, None, _("All your conversations has been deleted."))


class CreateMessageView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CreateMessageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            data = serializer.create(serializer.validated_data)
            return response(True, data)
        else:
            return response(False, None, serializer.errors)


class ConversationView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user, is_deleted=False
        ).order_by("-updated")

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MessageView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer
    pagination_class = None

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")
        return Message.objects.filter(
            conversation__user=self.request.user,
            is_deleted=False,
            conversation_id=conversation_id,
        ).order_by("created")

    def get(self, request, *args, **kwargs):
        data = self.list(request, *args, **kwargs).data
        return response(True, data)
