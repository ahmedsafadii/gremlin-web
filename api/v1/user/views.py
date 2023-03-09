from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from api.v1.user.serializer import (
    UpdateDeviceSerializer,
    UserSerializer,
    GoogleLoginSerializer,
    AppleLoginSerializer,
    SubscriptionSerializer,
)
from core.models import Conversation, Message, Plan
from core.models.user import UserTransaction, UserPlan
from gremlin.middleware import response
from django.utils.translation import gettext_lazy as _

from utils.appstore import SubscriptionManager, SubscriptionStatus


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
            user.conversations.delete()
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


class SubscriptionView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer

    def update_subscription_status(self, user, result):
        status = result.get("status")
        latest_receipt_info = result.get("latest_receipt_info")
        expiration_date = result.get("expiration_date")
        product_id = result.get("product_id")
        original_transaction_id = result.get("original_transaction_id")
        if latest_receipt_info is None:
            return False, "Unable to validate the receipt"

        plan = Plan.objects.get(bundle_id=product_id)
        user_plan_object, user_plan_created = UserPlan.objects.update_or_create(
            user=user, original_transaction_id=original_transaction_id
        )
        user_plan_object.plan = plan
        user_plan_object.type = SubscriptionStatus.VALID.value
        user_plan_object.expire_in = expiration_date
        user_plan_object.original_transaction_id = original_transaction_id

        if status == SubscriptionStatus.VALID:
            if not user_plan_object.is_active:
                amount = self._create_subscription_balance(
                    user=user, plan_tokens=plan.tokens
                )
                UserTransaction.objects.create_transaction(
                    user=user,
                    amount=amount,
                    is_credit=True,
                    is_gift=False,
                    is_free=False,
                    notes=f"New tokens for {original_transaction_id}",
                    original_transaction_id=original_transaction_id,
                )
            user_plan_object.is_active = True
            user_plan_object.save()
            return True, "You are now a Pro member of GenChat APP."
        elif status == SubscriptionStatus.EXPIRED:
            user_plan_object.is_active = False
            user_plan_object.save()
            return True, "Sorry but your subscription is expire."
        elif status == SubscriptionStatus.TRIAL:
            if not user_plan_object.is_active:
                amount = self._create_subscription_balance(
                    user=user, plan_tokens=plan.tokens
                )
                UserTransaction.objects.create_transaction(
                    user=user,
                    amount=amount,
                    is_credit=True,
                    is_gift=False,
                    is_free=False,
                    notes=f"New tokens for {original_transaction_id}",
                    original_transaction_id=original_transaction_id,
                )
            user_plan_object.is_active = True
            user_plan_object.save()
            return True, "You are now om a trial Pro member of GenChat APP."
        else:
            user_plan_object.is_active = False
            user_plan_object.save()
            return True, "Your subscription is not valid"

    @staticmethod
    def _create_subscription_balance(user, plan_tokens):
        balance = UserSerializer(user).data.get("balance", {}).get("balance", 0)
        return plan_tokens - balance

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            user = request.user
            receipt_data = serializer.validated_data.get("receipt")
            subscription_manager = SubscriptionManager()
            validate_result = subscription_manager.validate_receipt(receipt_data)
            status, message = self.update_subscription_status(
                user=user, result=validate_result
            )
            return response(status, UserSerializer(user).data, message)
        else:
            return response(False, None, serializer.errors)
