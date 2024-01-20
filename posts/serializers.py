from rest_framework import serializers
from .models import Post
from authentication.models import User
from django.forms.models import model_to_dict
from django.utils.timesince import timesince
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
        fields = ['caption','post_img']

class PostRetrieveSerializer(serializers.ModelSerializer):
    author_first_name = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['caption','post_img','author_first_name','created_at']
    def get_author_first_name(self, obj):
        # Assuming 'author' is a ForeignKey field in Post model linking to User model
        # Adjust the field names accordingly if they are different in your models
        return obj.author.first_name if obj.author else None

class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption']