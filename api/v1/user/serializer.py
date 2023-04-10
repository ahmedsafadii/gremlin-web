import jwt
import requests
from django.contrib.auth.models import User
from django.db.models import F, Sum
from rest_framework import serializers
from rest_framework.status import HTTP_200_OK
from django.utils.translation import gettext_lazy as _
from core.models import Device, GetStartedBot
from rest_framework.authtoken.models import Token
from core.models.user import UserTransaction
from utils.helper import get_apple_user, UserColorGenerator


class UpdateDeviceSerializer(serializers.Serializer):  # noqa
    deviceId = serializers.CharField(required=True, allow_blank=False)
    platform = serializers.CharField(required=True)
    language = serializers.CharField(required=True)
    oneSignal = serializers.CharField(required=False, allow_blank=True)
    appVersion = serializers.CharField(required=True, allow_blank=False)
    appBuild = serializers.CharField(required=True, allow_blank=False)
    latitude = serializers.CharField(required=False, allow_blank=True)
    longitude = serializers.CharField(required=False, allow_blank=True)

    def save(self, **kwargs):
        data = self.validated_data
        request = self.context.get("request")
        device_id = data.get("deviceId", "")
        device_object, device_created = Device.objects.update_or_create(
            device_id=device_id
        )
        GetStartedBot.objects.update_or_create(device=device_object)
        device_object.platform = data.get("platform", "")
        device_object.language = data.get("language", "")
        device_object.onesignal = data.get("oneSignal", "")
        device_object.app_version = data.get("appVersion", "")
        device_object.app_build = data.get("appBuild", "")
        device_object.sessions = F("sessions") + 1

        if request.user.is_authenticated:
            device_object.user = request.user

        device_object.save()
        return request.user


class TokenSerializer(serializers.StringRelatedField):  # noqa
    class Meta:
        model = Token
        fields = ["key"]


class UserSerializer(serializers.ModelSerializer):
    token = TokenSerializer(source="auth_token")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")
    userId = serializers.IntegerField(source="id")
    userColor = serializers.SerializerMethodField()
    nickName = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    claimGift = serializers.SerializerMethodField()
    userPlan = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "userId",
            "firstName",
            "lastName",
            "email",
            "token",
            "userColor",
            "nickName",
            "balance",
            "claimGift",
            "userPlan",
        ]

    @staticmethod
    def get_userPlan(obj):
        user_plan = obj.plans.filter(is_active=True)
        if user_plan.exists():
            user_plan = user_plan.first()
            return {
                "isActive": user_plan.is_active,
                "planId": user_plan.plan.id,
                "expireDate": user_plan.expire_in,
            }
        return {"isActive": False}

    @staticmethod
    def get_claimGift(obj):
        return obj.transactions.filter(is_gift=True).exists()

    @staticmethod
    def get_balance(obj):
        debit_subquery = obj.transactions.filter(
            is_credit=False,
        ).aggregate(debit=Sum("amount"))

        credit_subquery = obj.transactions.filter(
            is_credit=True,
        ).aggregate(credit=Sum("amount"))

        credit = credit_subquery["credit"] or 0
        debit = debit_subquery["debit"] or 0

        balance = credit - debit

        return {
            "debit": debit,
            "credit": credit,
            "balance": balance,
        }

    @staticmethod
    def get_nickName(obj, is_shortcut=True):
        # TODO: Need to find a good idea for the nickname in case there is more than 1 device
        nickname = (
            GetStartedBot.objects.filter(device__user=obj.id)
            .values_list("nickname", flat=True)
            .order_by("-created")
            .first()
        )
        if nickname:
            return nickname[0] if is_shortcut else nickname
        return None

    @staticmethod
    def get_userColor(obj):
        return UserColorGenerator.generate_user_color(obj.id)


class VisitorLoginSerializer(serializers.Serializer):  # noqa
    deviceId = serializers.CharField(allow_blank=False, required=True)

    @staticmethod
    def _check_or_retrieve(user_id):
        username = "d-%s" % user_id
        if not username or username == "":
            raise serializers.ValidationError({"auth": _("Device id is missing")})
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return False

    @staticmethod
    def _create_user_as_visitor(user_id, email, first_name, last_name):
        username = "d-%s" % user_id
        user_object = User()
        user_object.is_active = True
        user_object.username = username
        user_object.email = email
        user_object.first_name = first_name
        user_object.last_name = last_name
        user_object.save()
        return user_object

    @staticmethod
    def add_free_credits(user):
        if not UserTransaction.objects.filter(user=user, is_free=True).exists():
            UserTransaction.objects.create_free_transaction(user=user)

    def save(self, **kwargs):
        device_id = self.validated_data.get("deviceId")
        user_id = device_id
        email = device_id + "@chatgx.com"
        first_name = ""
        last_name = ""

        user = self._check_or_retrieve(user_id=user_id)

        if not user:
            user = self._create_user_as_visitor(
                user_id=user_id, email=email, first_name=first_name, last_name=last_name
            )
        user.is_active = True
        user.save()
        self.add_free_credits(user=user)
        Token.objects.update_or_create(user=user)

        if device_id:
            Device.objects.filter(device_id=device_id).update(user=user)

        return UserSerializer(user).data


class GoogleLoginSerializer(serializers.Serializer):  # noqa
    accessToken = serializers.CharField(allow_blank=False, required=True)
    deviceId = serializers.CharField(allow_blank=False, required=True)

    @staticmethod
    def _request_google_user(token):
        google_url = (
            f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}"
        )
        google_request = requests.get(google_url)
        if google_request.status_code == HTTP_200_OK:
            return google_request.json()
        else:
            raise serializers.ValidationError(
                {"auth": [_("Unable to fetch google info data")]}
            )

    @staticmethod
    def add_free_credits(user):
        if not UserTransaction.objects.filter(user=user, is_free=True).exists():
            UserTransaction.objects.create_free_transaction(user=user)

    @staticmethod
    def _check_or_retrieve(user_id):
        username = "google-%s" % user_id
        if not username or username == "":
            raise serializers.ValidationError({"auth": _("Google id is missing")})
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return False

    @staticmethod
    def _create_user(user_id, email, first_name, last_name):
        username = "google-%s" % user_id
        user_object = User()
        user_object.is_active = True
        user_object.username = username
        user_object.email = email
        user_object.first_name = first_name
        user_object.last_name = last_name
        user_object.save()
        return user_object

    def save(self, **kwargs):
        access_token = self.validated_data.get("accessToken")
        device_id = self.validated_data.get("deviceId")
        google_data = self._request_google_user(access_token)
        user_id = google_data.get("sub")
        email = google_data.get("email")
        first_name = google_data.get("given_name", "")
        last_name = google_data.get("family_name", "")

        user = self._check_or_retrieve(user_id=user_id)

        if not user:
            user = self._create_user(
                user_id=user_id, email=email, first_name=first_name, last_name=last_name
            )
        user.is_active = True
        user.save()
        self.add_free_credits(user=user)
        Token.objects.update_or_create(user=user)

        if device_id:
            Device.objects.filter(device_id=device_id).update(user=user)

        return UserSerializer(user).data


class AppleLoginSerializer(serializers.Serializer):  # noqa
    accessToken = serializers.CharField(allow_blank=False, required=True)
    deviceId = serializers.CharField(allow_blank=False, required=True)

    @staticmethod
    def _get_apple_user(access_token):
        access_token_url = "https://appleid.apple.com/auth/token"

        client_id, client_secret = get_apple_user()
        headers = {"content-type": "application/x-www-form-urlencoded"}

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": access_token,
            "grant_type": "authorization_code",
        }
        res = requests.post(access_token_url, data=data, headers=headers)
        response_dict = res.json()
        id_token = response_dict.get("id_token", None)
        if id_token:
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            return decoded
        else:
            raise serializers.ValidationError(
                {"auth": [_("Unable to fetch apple info data")]}
            )

    @staticmethod
    def _check_or_retrieve(user_id):
        username = "apple-%s" % user_id
        if not username or username == "":
            raise serializers.ValidationError({"auth": _("Apple id is missing")})
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return False

    @staticmethod
    def _create_user(user_id, email, first_name, last_name):
        username = "apple-%s" % user_id
        user_object = User()
        user_object.is_active = True
        user_object.username = username
        user_object.email = email
        user_object.first_name = first_name
        user_object.last_name = last_name
        user_object.save()
        return user_object

    def save(self, **kwargs):
        access_token = self.validated_data.get("accessToken")
        apple_user_data = self._get_apple_user(access_token=access_token)
        device_id = self.validated_data.get("deviceId")

        email = apple_user_data.get("email")
        user_id = str(apple_user_data.get("sub"))

        user = self._check_or_retrieve(user_id=user_id)

        if not user:
            user = self._create_user(
                user_id=user_id, email=email, first_name="Apple", last_name=user_id
            )
        GoogleLoginSerializer.add_free_credits(user=user)
        Token.objects.update_or_create(user=user)

        user.is_active = True
        user.save()

        if device_id:
            Device.objects.filter(device_id=device_id).update(user=user)

        return UserSerializer(user).data


class SubscriptionSerializer(serializers.Serializer):  # noqa
    receipt = serializers.CharField(required=True, allow_null=False)
