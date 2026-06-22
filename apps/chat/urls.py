"""
URL patterns for chat app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Conversations
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', views.MessageListView.as_view(), name='messages'),
    path('conversations/<int:conversation_id>/read/', views.mark_conversation_read, name='mark-read'),

    # Direct messages
    path('dm/<str:username>/', views.start_direct_message, name='start-dm'),
]
