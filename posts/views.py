from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, status, generics,viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db import transaction,IntegrityError
from .serializers import (PostSerializer,PostUpdateSerializer,PostRetrieveSerializer,CommentSerializer,
CommentretrieveSerializer,SavedPostSerializer,NotificationSerializer,RetrieveSavedPostSerializer)
from .models import Post,Comment,SavedPost,Notification,Reportedposts
from authentication.models import User,Follow
from authentication.serializers import UserSerializer
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
        # Get the authors followed by the current user
        followed_authors = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        followed_authors = list(followed_authors)
        followed_authors.append(request.user.id)
        # Filter the queryset to get posts authored by followed users
        queryset = Post.objects.filter(author__in=followed_authors,is_blocked=False).order_by('-created_at')
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
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, postId, format=None):
        print(request,"huuuuuurrrrrrrraaaaayyyyyyy")
        try:
            instance = Post.objects.get(pk=postId)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        

class UserPostUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
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
                if not post.author == user:
                    Notification.objects.create(
                        from_user=user,
                        to_user=post.author,
                        post=post,
                        notification_type=Notification.NOTIFICATION_TYPES[0][0],
                    )
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

class SavePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request,pk):
        try:
            post = Post.objects.get(id=pk)
            user = request.user

            saved_post = SavedPost.objects.create(user=user, post=post)
            serializer = SavedPostSerializer(saved_post)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)     
        except IntegrityError:
            return Response({"error": "SavedPost already exists for this user and post."}, status=status.HTTP_400_BAD_REQUEST)

class RetrieveSavedPosts(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        try:
            posts = SavedPost.objects.filter(user=request.user)
            serializer = RetrieveSavedPostSerializer(posts,many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND) 
            
class NotificationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(to_user=user).exclude(is_seen=True).order_by('-created')

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationsSeenView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def post(self, request, pk, *args, **kwargs):
        try:
            notification = Notification.objects.get(pk=pk)
            notification.is_seen = True
            notification.save()
            return Response(status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response("Not found in database", status=status.HTTP_404_NOT_FOUND)

# this api is to help user to report a post
class ReportPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self,request,pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response("Post does not exist",status=status.HTTP_404_NOT_FOUND)
        user = request.user
        Reportedposts.objects.create(author=user,post=post)
        return Response("Post reported successfully",status=status.HTTP_200_OK)

# this api is to fetch all the post if the count of 'reported_by_user' field is greater than 0, which simply means give
# all the reported posts to admin
class FetchReportedPostsForAdmin(APIView):
    serializer_class = PostRetrieveSerializer
    def get(self,request):
        post             = Post.objects.annotate(num_of_reports=Count('reported_by_users')).filter(num_of_reports__gt=0)
        serialized_posts = self.serializer_class(post,many=True)
        return Response(serialized_posts.data,status=status.HTTP_200_OK)


# the two api's written below helps the admin to block and unblock a post
class BlockAPost(APIView):
    def post(self,request,pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response("Post doesnt exist",status=status.HTTP_404_NOT_FOUND)
        post.is_blocked = True
        post.save()
        return Response("Blocked Successfully",status=status.HTTP_200_OK)

class UnblockAPost(APIView):
    def post(self,request,pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response("Post doesnt exist",status=status.HTTP_404_NOT_FOUND)
        post.is_blocked = False
        post.save()
        return Response("Unblocked Successfully",status=status.HTTP_200_OK)