from rest_framework.views import APIView
from rest_framework import status,permissions
from django.contrib.auth import get_user_model,authenticate
from .models import Follow
from posts.models import Post
from posts.serializers import PostRetrieveSerializer
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import timedelta 
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from rest_framework import status,generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import(UserSignupSerializer,UserSerializer,GoogleUserSerializer,UserRetrieveSerializer)
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
import jwt
from django.db.models import Q, Count
from .tasks import (welcomemail,otp)
from django.db import transaction



# Create your views here


User = get_user_model()

class Signup(APIView):
    def post(self,request):
        data            = request.data
       
        user_serializer = UserSignupSerializer(data = data)
        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        user            = user_serializer.create(user_serializer.validated_data)
        user.is_active  = False
        user.save()
        serializer      = UserSerializer(user)
        user            = serializer.data

        email = request.data.get('email', None)
        #calling the celery task to send otp to the user
        otp_result=otp.delay(user['email'])
        otp_value = otp_result.get()
        user = User.objects.get(email=email)
        user.otp = otp_value
        user.save()

        return Response({"detail": "OTP sent successfully","email":email}, status=status.HTTP_200_OK)



class VerifyOTP(APIView):
    def post(self, request):

        entered_otp = request.data.get('Otp', '')
        
        user_mail = request.data.get('email')

        if not user_mail:
            return Response({"detail": "User mail not found in request"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(email=user_mail)  # Replace YourUserModel with your actual User model

        stored_otp = user.otp
        
       

        
        if entered_otp == stored_otp:
            user.is_active = True
            user.otp = None
            user.save()

            serializer = UserSerializer(user)
            user_data = serializer.data

            # Call the Celery task after successful user registration
            welcomemail.delay(user_data['email'])

            return Response({"detail": "User registered successfully"}, status=status.HTTP_200_OK)
        else:
            user = User.objects.get(email=user_mail)
            user.delete()
            return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


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

        if user and user.is_blocked == True:
            return Response({"Blocked" : "This account is blocked!!"}, status=status.HTTP_404_NOT_FOUND)


        elif user is not None:
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
        token = data.get('token')

        
        if token:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)

                if user.is_blocked == True:
                    return Response({"Blocked" : "This account is blocked!!"}, status=status.HTTP_404_NOT_FOUND)

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
                    

                            response.data = {"Success" : "Login successfully","data":data}
                            return response 
        else:
             status = {"TOKENNOTFOUND" : "AUTHENTICATION FAILED"}
             return Response(status)             



class Retrieveuserdetails(APIView):
    def get(self,request):
        user = User.objects.exclude(is_staff=True)
        serializer = UserRetrieveSerializer(user,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class FollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, email):
        try:
            following = User.objects.get(email=email)
            follower = request.user
            follow_instance = Follow.objects.filter(following=following, follower=follower).first()
            # print(following)
            # print(follower)
            if follow_instance:
                # Unfollow 
                with transaction.atomic():
                    follow_instance.delete()
                return Response("Unfollowed", status=status.HTTP_200_OK)
            else:
                # Follow 
                with transaction.atomic():
                    follow = Follow(following=following, follower=follower)
                    follow.save()
                return Response("Followed", status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FollowListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        queryset = User.objects.filter(Q(followers__follower=current_user) & ~Q(id=current_user.id))
        return queryset
    



class FollowerListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        queryset = User.objects.filter(Q(following__following=current_user) & ~Q(id=current_user.id))
        return queryset

# the below provided api is to check if the user is blocked in regular intervals of time>
class UserStatus(APIView):
    def get(self,request,email):
        print(email,"EEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
        user = User.objects.get(email=email)
        if user.is_blocked == True:
            status = {"BLOCKED" : "user is blocked"}
            return Response(status)
        else:
            status = {"NOTBLOCKED" : "user is not blocked"}
            return Response(status)

# this api is to give the user data to the frontend
class UserRetrieveView(APIView):
    def get(self,request,email):
            user = User.objects.get(email=email)
            serializer = UserRetrieveSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)

# this api is to give the users post to the userprofile
class UserPostRetrieve(APIView):
    def get(self,request,email):
        user = User.objects.get(email=email)
        post = Post.objects.filter(author=user)
        serializer = PostRetrieveSerializer(post,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

