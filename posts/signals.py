from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, Comment
from .serializers import NotificationSerializer
import json


@receiver(post_save, sender=Notification)
def notification_post_save_handler(sender, instance, created, **kwargs):
    print("Signals ++++++++++ ", instance)
    user = instance.to_user
    if user and created:
        channel_layer = get_channel_layer()
        count = Notification.objects.filter(is_seen=False, to_user=user).count()
        serialized_instance = NotificationSerializer(instance).data
        async_to_sync(channel_layer.group_send)(
            f"notify_{user.id}",
            {
                "type": "send_notification",
                "value": json.dumps(serialized_instance),
            }
        )


@receiver(post_save, sender=Comment)
def create_commen_notification(sender, instance, created, **kwargs):
    if created:
        # Check if the commenter is not the author of the post
        if instance.user != instance.post.author:
            Notification.objects.create(
                from_user=instance.user,
                to_user=instance.post.author,
                post=instance.post,
                comment=instance,
                notification_type=Notification.NOTIFICATION_TYPES[3][0],
            )



