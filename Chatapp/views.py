from django.shortcuts import render 
from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from authentication.models import User,Follow
from authentication.serializers import UserSerializer
from django.db.models import Q
from django.contrib.auth import get_user_model

from.models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer, ChatRoomListSerializer
# Create your views here.

User = get_user_model()

class CreateChatRoom(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer
 
    def post(self, request, pk):
        current_user = request.user
        other_user = User.objects.get(pk=pk)

        # Check if a chat room already exists between the users
        existing_chat_rooms = ChatRoom.objects.filter(members=current_user).filter(members=other_user)
        if existing_chat_rooms.exists():
            serializer = ChatRoomSerializer(existing_chat_rooms.first())
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create a new chat room
        chat_room = ChatRoom()
        chat_room.save()
        chat_room.members.add(current_user, other_user)
        
        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoomMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
 
    def get(self, request, pk):
        
        try:
            room = ChatRoom.objects.get(pk=pk)
            messages = Message.objects.filter(room=room)
            serialized_messages = self.serializer_class(messages, many=True).data
            return Response(serialized_messages, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            return Response("Room not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(members=user)

class ContactListAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        user = request.user
        followed_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        contactlist = User.objects.filter(id__in=followed_users)
        serializer = UserSerializer(contactlist, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)