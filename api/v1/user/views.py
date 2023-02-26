from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from api.v1.user.serializer import (
    UpdateDeviceSerializer,
    UserSerializer,
    GoogleLoginSerializer,
    AppleLoginSerializer,
)
from core.models import Conversation, Message
from core.models.user import UserTransaction
from gremlin.middleware import response
from django.utils.translation import gettext_lazy as _


class UpdateDeviceView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UpdateDeviceSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return response(True, None)
        else:
            return response(False, None, serializer.errors)


class GoogleLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):  # noqa
        serializer = GoogleLoginSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            return response(True, user)
        else:
            return response(False, None, serializer.errors)


class AppleLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):  # noqa
        serializer = AppleLoginSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            return response(True, user)
        else:
            return response(False, None, serializer.errors)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):  # noqa
        profile_ser = UserSerializer(request.user)
        return response(True, profile_ser.data)


class DeleteAccountView(APIView):
    permission_classes = (IsAuthenticated,)

    def _change_user_to_deactivate(self):
        with transaction.atomic():
            user = self.request.user
            user.is_active = False
            user.save()
            user.auth_token.delete()
            user.devices.all().delete()
            conversations = Conversation.objects.select_related("user").filter(
                user=user
            )
            messages = Message.objects.select_related("conversation__user").filter(
                conversation__user=user
            )
            conversations.update(is_deleted=True)
            messages.update(is_deleted=True)

    def post(self, request):  # noqa
        # We need to change the email and username for deleted+userid++email
        self._change_user_to_deactivate()
        return response(
            True,
            None,
            _("Your account has been deleted, you will automatically logout"),
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):  # noqa
        request.user.auth_token.delete()
        return response(True, None, _("Successfully logged out."))


class ClaimRatingGiftView(APIView):
    permission_classes = (IsAuthenticated,)

    def _assign_user_gift(self):
        user = self.request.user
        if not UserTransaction.objects.filter(user=user, is_gift=True).exists():
            UserTransaction.objects.create_rating_gift_transaction(user=user)
        return user

    def post(self, request):  # noqa
        user = self._assign_user_gift()
        return response(True, UserSerializer(user, many=False).data)
