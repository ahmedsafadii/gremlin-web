from api.v1.assistant import views
from django.urls import path

urlpatterns = [
    path("get_started", views.GetStartedView.as_view()),
    path("get_started_history", views.GetStartedHistoryView.as_view()),
    path("prompts", views.PromptsListView.as_view()),
    path("public_lobby", views.PublicLobbyListView.as_view()),
    path("conversation", views.ConversationView.as_view()),
    path("create_message", views.CreateMessageView.as_view()),
    path("delete_all_conversation", views.DeleteConversationView.as_view()),
    path("clear_conversation", views.ClearConversationView.as_view()),
    path(
        "save_conversation/<int:conversation_id>/", views.SaveConversationView.as_view()
    ),
    path("messages/<int:conversation_id>/", views.MessageView.as_view()),
]
