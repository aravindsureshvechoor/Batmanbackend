"""
ASGI config for batman project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from .channelsmiddleware import JwtAuthMiddleware
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from Chatapp.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'batman.settings')
from posts.routing import websocket_urlpatterns as notification_url

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': JwtAuthMiddleware(
            AllowedHostsOriginValidator(URLRouter(websocket_urlpatterns+notification_url))
        )
    }
)
