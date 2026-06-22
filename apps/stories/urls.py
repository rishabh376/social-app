from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.ActiveStoriesView.as_view(), name='stories-feed'),
    path('my/', views.MyStoriesView.as_view(), name='my-stories'),
    path('<int:story_id>/view/', views.ViewStoryView.as_view(), name='view-story'),
]
