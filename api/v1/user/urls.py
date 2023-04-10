from api.v1.user import views
from django.urls import path

urlpatterns = [
    path("update_device", views.UpdateDeviceView.as_view()),
    path("login_as_visitor", views.VisitorLoginView.as_view()),
    path("login_with_google", views.GoogleLoginView.as_view()),
    path("login_with_apple", views.AppleLoginView.as_view()),
    path("profile", views.ProfileView.as_view()),
    path("delete_account", views.DeleteAccountView.as_view()),
    path("claim_rating_gift", views.ClaimRatingGiftView.as_view()),
    path("logout", views.LogoutView.as_view()),
    path("validate_subscription", views.SubscriptionView.as_view()),
]
