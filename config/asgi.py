"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Only import after setting up Django environment
django_asgi_app = get_asgi_application()

# Delay imports that depend on Django setup
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import URLRouter
from apps.notifications.middleware import JWTAuthMiddleware
import apps.notifications.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(
                apps.notifications.routing.websocket_urlpatterns
            )
        )
    ),
})
