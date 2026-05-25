import jwt
import time
from django.conf import settings

def get_centrifugo_token(user_id):
    sub = str(user_id) if user_id else ""

    payload = {
        "sub": sub,
        "exp": int(time.time()) + 3600
    }

    return jwt.encode(payload, settings.CENTRIFUGO_TOKEN_SECRET, algorithm="HS256")
