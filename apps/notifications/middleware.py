from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from urllib.parse import parse_qs

@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from query string
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]
        
        scope["user"] = AnonymousUser()
        
        if token:
            try:
                # Decode the JWT token
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )
                user_id = payload.get("user_id")
                if user_id:
                    scope["user"] = await get_user(user_id)
            except (InvalidTokenError, ExpiredSignatureError):
                pass
        
        return await super().__call__(scope, receive, send)