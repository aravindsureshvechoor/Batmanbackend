from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, status, generics,viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db import transaction
from .serializers import (PostSerializer,PostUpdateSerializer,PostRetrieveSerializer)
from .models import Post
from authentication.models import User


# Create your views here.
class CreatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            
            post_img = request.data['post_img']
            caption = request.data['caption']
            
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                post = serializer.save(author=user, post_img=post_img, caption=caption)
                
                # Serialize the created post instance
                serialized_post = self.serializer_class(instance=post)
            
                return Response(serialized_post.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:
            

            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

class ListPostOnUserSide(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        queryset = Post.objects.all()
        serializer = PostRetrieveSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class UserPostDeleteView(APIView):
    def delete(self, request, pk, format=None):
        try:
            instance = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

class UserPostUpdateView(APIView):
    def put(self, request, pk, format=None):
        try:
            instance = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostUpdateSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)