from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, status, generics,viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db import transaction
from .serializers import (PostSerializer,PostUpdateSerializer,PostRetrieveSerializer,CommentSerializer,
CommentretrieveSerializer)
from .models import Post,Comment,SavedPost
from authentication.models import User
import json

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
        queryset = Post.objects.all().order_by('-created_at')
        serializer = PostRetrieveSerializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

# //////////////BELOW API IS TO DISPLAY A SINGLE POST ON COMMENT SECTION
class ListSinglePostOnUserSide(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request,pk):
        post = Post.objects.get(id=pk)
        serializer = PostRetrieveSerializer(post)
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


class LikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(id=pk)
            user = request.user
            if user in post.likes.all():
                post.likes.remove(user)
                return Response("Like removed", status=status.HTTP_200_OK)
            else:
                post.likes.add(user) 
                likeCount = post.total_likes()
                responsedata= {"msg":"Like added", "likeCount":likeCount}
                return Response(responsedata, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            user = request.user
            body = request.data.get('body')
            print(request.data, body)
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, post_id=pk, body=body)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

class DeleteCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(id=pk, user=request.user)
            comment.delete()                        
            return Response("Comment deleted successfully",status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("Not found in database", status=status.HTTP_404_NOT_FOUND)


class GetCommentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,pk):        
        comments = Comment.objects.filter(post_id=pk)
        serializer =CommentretrieveSerializer(comments,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

# this api is to save post to users collection
# class SavePosts(APIView):
#     def post(self,request, *args, **kwargs):
#         user = request.user
#         post = 
        
            
            
            