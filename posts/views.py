from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import permissions, status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Q, Count
from django.db import transaction
from .serializers import (PostSerializer)
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
            print("++++++++++++++  ",request.data)
            post_img = request.data['post_img']
            caption = request.data['caption']
            print("++++++++++++++  ",request.data)
            print("GGGGGGGGGGGGGGGGGGGGGGGG",post_img)
            print("mmmmmmmmmmmmmmmmmmmmm",caption)
            serializer = self.serializer_class(data=request.data)
            print(serializer.is_valid(),"****************************")
            if serializer.is_valid():
                post = serializer.save(author=user, post_img=post_img, caption=caption)
                
                # Serialize the created post instance
                serialized_post = self.serializer_class(instance=post)
            
                return Response(serialized_post.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            
        except Exception as e:

            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)