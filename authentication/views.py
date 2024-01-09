from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import(UserSignupSerializer,UserSerializer)
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
import jwt

# Create your views here


User = get_user_model()

class Signup(APIView):
    def post(self,request):
        data            = request.data
        user_serializer = UserSignupSerializer(data = data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        user            = user_serializer.create(user_serializer.validated_data)
        user.is_active  = True
        user.save()
        serializer      = UserSerializer(user)
        user            = serializer.data

        return Response(user, status=status.HTTP_201_CREATED)