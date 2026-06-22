"""
URL patterns for notifications app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notifications'),
    path('unread-count/', views.UnreadNotificationsCountView.as_view(), name='unread-count'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('<int:notification_id>/read/', views.mark_notification_read, name='mark-read'),
]
