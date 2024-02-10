from rest_framework import serializers
from .models import Post,Comment,SavedPost
from authentication.models import User
from . models import Notification
from django.forms.models import model_to_dict
from django.utils.timesince import timesince
from authentication.serializers import UserSerializer
import os


class PostSerializer(serializers.ModelSerializer):
    

    def get_likes_count(self, obj):
        return obj.total_likes()
    
    def get_reports_count(self, obj):
        return obj.total_reports()

    
    def validate_post_img(self, value):
        max_size = 1.5 * 1024 * 1024  # 1.5 MB in bytes

        if value.size > max_size:
            raise serializers.ValidationError('The image size should not exceed 1.5 MB.')

        valid_extensions = ['.jpg', '.jpeg', '.png', '.svg']
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in valid_extensions:
            raise serializers.ValidationError('Invalid image file type. Supported formats: jpg, jpeg, png, svg.')

        return value

    class Meta:
        model = Post
        fields = ['caption','post_img','total_likes','id']
        

class PostRetrieveSerializer(serializers.ModelSerializer):
    author_first_name = serializers.SerializerMethodField()
    author_last_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id','author_email','caption','post_img','author_first_name','author_last_name','likes','created_at','total_likes']
    def get_author_first_name(self, obj):
        return obj.author.first_name if obj.author else None
    def get_author_last_name(self, obj):
        return obj.author.last_name if obj.author else None
    def get_author_email(self,obj):
        return obj.author.email if obj.author else None

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    created = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [ 'id','user', 'body', 'created' ]
    
    def get_created(self, obj):
        return timesince(obj.created)

class CommentretrieveSerializer(serializers.ModelSerializer):
    user_first_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id','body','created','user_first_name']
    def get_user_first_name(self, obj):
        # Assuming 'author' is a ForeignKey field in Post model linking to User model
        # Adjust the field names accordingly if they are different in your models
        return obj.user.first_name if obj.user else None
    
class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = SavedPost
        fields = '__all__'

class RetrieveSavedPostSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField()
    # us_er = serializers.SerializerMethodField()

    class Meta:
        model = SavedPost
        fields = ['post']

    def get_post(self, obj):
        # Assuming you have a serializer for the Post model called PostSerializer
        post_serializer = PostSerializer(obj.post)
        return post_serializer.data

    # def get_us_er(self, obj):
    #     # Assuming you have a serializer for the User model called UserSerializer
    #     user_serializer = UserSerializer(obj.user)
    #     return user_serializer.data

class UserNotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')

class NotificationSerializer(serializers.ModelSerializer):
    from_user = UserNotifySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('notification_type',)

    def validate_notification_type(self, value):
        choices = dict(Notification.NOTIFICATION_TYPES)
        if value not in choices:
            raise serializers.ValidationError("Invalid notification type.")
        return value
