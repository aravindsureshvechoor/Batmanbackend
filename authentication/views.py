from rest_framework.views import APIView
from rest_framework import status,permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .serializers import(UserSignupSerializer,UserSerializer,MyTokenObtainPairSerializer)
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)  # Call the parent class's post method
        except InvalidToken as e:
            response = Response({'detail': str(e)}, status=e.status_code)
        return response