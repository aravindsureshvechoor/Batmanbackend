from django.urls import path
from .views import CreatePostView,ListPostOnUserSide,UserPostDeleteView,UserPostUpdateView,LikeView

urlpatterns = [
    path('create/', CreatePostView.as_view()), 
    path('get/', ListPostOnUserSide.as_view()),
    path('delete/<int:pk>/', UserPostDeleteView.as_view()),  
    path('update/<int:pk>/', UserPostUpdateView.as_view()),  
    path('like/<int:pk>/', LikeView.as_view()),  
]