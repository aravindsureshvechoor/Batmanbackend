from rest_framework import serializers
from django.utils.timesince import timesince

class ChatRoomSerializer(serializers.ModelSerializer):
    from .models import ChatRoom  # Moved import inside the serializer

    class Meta:
        model = ChatRoom
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    from .models import Message  # Moved import inside the serializer
    from authentication.models import User  # Moved import inside the serializer

    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    created = serializers.SerializerMethodField(read_only=True)
    sender_first_name = serializers.SerializerMethodField(read_only=True)
    sender_profile_image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Message
        fields = ['room', 'sender_profile_image','sender', 'content', 'timestamp', 'is_seen', 'sender_email', 'created', 'sender_first_name']

    def get_created(self, obj):
        return timesince(obj.timestamp)

    def get_sender_first_name(self, obj):
        return obj.sender.first_name if obj.sender else None
    
    def get_sender_profile_image(self, obj):
        return obj.sender.profile_image.url if obj.sender and obj.sender.profile_image else None

class UserSerializer(serializers.ModelSerializer):
    from authentication.models import User  # Moved import inside the serializer

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_image']

class ChatRoomListSerializer(serializers.ModelSerializer):
    from .models import ChatRoom, Message  # Moved import inside the serializer
    from authentication.models import User  # Moved import inside the serializer

    unseen_message_count = serializers.SerializerMethodField()
    members = UserSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = '__all__'

    def get_unseen_message_count(self, obj):
        user = self.context['request'].user
        return Message.objects.filter(room=obj, is_seen=False).exclude(sender=user).count()

    def to_representation(self, instance):
        user = self.context['request'].user
        members = instance.members.exclude(id=user.id)
        data = super(ChatRoomListSerializer, self).to_representation(instance)
        data['members'] = UserSerializer(members, many=True).data
        return data
