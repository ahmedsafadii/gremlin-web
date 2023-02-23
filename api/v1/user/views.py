from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from api.v1.user.serializer import (
    UpdateDeviceSerializer,
    UserSerializer,
    GoogleLoginSerializer,
    AppleLoginSerializer,
)
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
        user = self.request.user
        deleted_user = f"d-{user.id}+{user.username}"
        updates = {
            "username": deleted_user,
            "email": deleted_user,
            "is_active": False,
        }
        user.auth_token.delete()
        # Device.objects.filter(user=user).delete()
        user.__class__.objects.filter(pk=user.pk).update(**updates)

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
