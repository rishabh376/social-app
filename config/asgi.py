"""
ASGI config for social-app.
Handles both HTTP and WebSocket connections.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

from apps.chat.routing import websocket_urlpatterns
from apps.notifications.routing import notification_urlpatterns

# Combine all websocket routes
all_websocket_patterns = websocket_urlpatterns + notification_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(all_websocket_patterns)
    ),
})
