from rest_framework.views import APIView
from rest_framework import status,permissions
from django.contrib.auth import get_user_model,authenticate
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import timedelta 
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import(UserSignupSerializer,UserSerializer,GoogleUserSerializer)
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
import jwt
from .tasks import (welcomemail)


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

        # Call the Celery task after successful user registration
        welcomemail.delay(user['email'])

        return Response(user, status=status.HTTP_201_CREATED)


#this is nothing but a function to generate tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



@method_decorator(csrf_exempt, name='dispatch')
class UserLogin(APIView):
    def post(self, request, format=None):
        data = request.data
        response = Response()
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                response = JsonResponse({
                    "data": data,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.first_name,
                    }
                })
                response.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value = data["access"],
                    expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )

                response.data = {"Success" : "Login successfully","data":data}
                return response
            else:
                return Response({"No active" : "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Invalid" : "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class GoogleAuth(APIView):
    def post(self, request):
        data = request.data
        print('*****', data)
        email = data.get('email', None)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user is not None:
                if user.is_active:
                    data = get_tokens_for_user(user)
                    response = JsonResponse({
                        "data": data,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "name": user.first_name,
                        }
                    })
                    response.set_cookie(
                        key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                        value = data["access"],
                        expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                        secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                        httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                        samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                    )
                
                    response.data = {"Success" : "Login successfully","data":data}
                    return response
        else:
            serializer = GoogleUserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if user is not None:
                    if user.is_active:
                        data = get_tokens_for_user(user)
                        response = JsonResponse({
                            "data": data,
                            "user": {
                                "id": user.id,
                                "email": user.email,
                                "name": user.first_name,
                            }
                        })
                        response.set_cookie(
                            key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                            value = data["access"],
                            expires = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                            secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                            httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                            samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                        )

                        response.data = {"Success" : "Login successfully","data":data}
                        return response 


