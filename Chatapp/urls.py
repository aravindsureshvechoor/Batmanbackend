from django.urls import path
from .views import CreateChatRoom, RoomMessagesView, ChatRoomListView

urlpatterns = [
    path('create-room/<int:pk>/', CreateChatRoom.as_view()),
    path('chat-room/<int:pk>/', RoomMessagesView.as_view()),
    path('chatrooms/', ChatRoomListView.as_view()),
]
