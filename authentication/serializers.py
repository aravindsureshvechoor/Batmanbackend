from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.exceptions import ValidationError as DRFValidationError
import os




User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['email', 'first_name', 'last_name', 'age', 'password']

    def validate(self,data):
        user     = User(**data)
        password = data.get('password')

        try:
            validate_password(password, user)
        except DRFValidationError as e:
            serializer_errors = serializers.as_serializer_error(e)
            raise DRFValidationError(
                {'password': serializer_errors['non_field_errors']}
            )

        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email      = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
            age        = validated_data['age'],
            password   = validated_data['password'],
        )
        return user

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model  = User
        fields = '__all__'

    def validate_profile_image(self, value):
        max_size = 1.5 * 1024 * 1024  # 1.5 MB in bytes

        if value.size > max_size:
            raise serializers.ValidationError('The image size should not exceed 1.5 MB.')

        valid_extensions = ['.jpg', '.jpeg', '.png', '.svg']
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise serializers.ValidationError('Invalid image file type. Supported formats: jpg, jpeg, png, svg.')

        return value

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if user.is_active:
            token = super().get_token(user)
            # Add custom claims
            return token
        else:
            if user.is_online:
                # User is not online, customize the response or raise an exception
                raise InvalidToken("Your account has been blocked.")
            else:
                raise InvalidToken("Please verify your email id.")