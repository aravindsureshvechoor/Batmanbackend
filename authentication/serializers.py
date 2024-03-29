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
from django.apps import apps




User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['email', 'first_name', 'last_name','password','gender','otp']

    email = serializers.EmailField()

    def validate_email(self, value):
        # Use Django's built-in EmailValidator for basic email format validation
        from django.core.validators import EmailValidator
        email_validator = EmailValidator(message="Enter a valid email address.")

        try:
            # This will raise a ValidationError if the email is not valid
            email_validator(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Custom email validation failed. Please provide a valid email.")


        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email      = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
            gender       = validated_data['gender'],
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

class GoogleUserSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = User
        fields = ['id','email']

    
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        # first_name = validated_data.pop('name')
        user = User.objects.create(**validated_data)
        user.email = email
        # user.first_name = first_name
        user.save()
        return user

class UserRetrieveSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id','email','first_name','last_name','is_blocked','profile_image','follower_count','following_count','post_count']
    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_post_count(self, obj):
        Post = apps.get_model('posts', 'Post')
        return Post.objects.filter(author=obj).count()

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','profile_image']
