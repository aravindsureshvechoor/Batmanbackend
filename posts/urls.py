from django.urls import path
from .views import CreatePostView

urlpatterns = [
    path('create/', CreatePostView.as_view()),       
]