from api.v1.app import views
from django.urls import path

urlpatterns = [
    path("tools", views.Tools.as_view()),
]
