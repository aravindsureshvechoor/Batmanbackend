from django.urls import path
from .views import (CreatePostView,ListPostOnUserSide,UserPostDeleteView,UserPostUpdateView,
LikeView,CreateCommentView,DeleteCommentView,ListSinglePostOnUserSide,GetCommentsView,SavePostView,NotificationsView,
NotificationsSeenView)


urlpatterns = [
    path('create/', CreatePostView.as_view()), 
    path('get/', ListPostOnUserSide.as_view()),
    path('singlepostforcomment/<int:pk>/', ListSinglePostOnUserSide.as_view()),
    path('delete/<int:pk>/', UserPostDeleteView.as_view()),  
    path('update/<int:pk>/', UserPostUpdateView.as_view()),  
    path('like/<int:pk>/', LikeView.as_view()),  
    path('comment/<int:pk>/', CreateCommentView.as_view(), name='comment-post'),
    path('deletecomment/<int:pk>/', DeleteCommentView.as_view(), name='delete-comment'),
    path('retrievecomments/<int:pk>/', GetCommentsView.as_view(), name='retrieve-comment'),
    path('savepost/<int:pk>/', SavePostView.as_view(), name='save-post'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications-seen/<int:pk>/', NotificationsSeenView.as_view(), name='notifications-seen'),
]