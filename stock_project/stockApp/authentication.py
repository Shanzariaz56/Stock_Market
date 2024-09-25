import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User
from functools import wraps

SECRET_KEY = settings.SECRET_KEY  
ALGORITHM = 'HS256'

# Generate a JWT token
def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(hours=12)  # Token expires in 12 hours
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Decode and verify the JWT token
def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Custom authentication function
def user_authentication(username, password):
    """
    Authenticates the user and returns a JWT token if successful.
    """
    user = authenticate(username=username, password=password)
    if user is not None:
        token = generate_jwt(user)
        return token
    return None

# JWT decorator for protecting views
def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Try to extract token from the Authorization header
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Fallback to query parameter
            token = request.GET.get('token')
        if not token:
            return JsonResponse({'error': 'Token missing'}, status=401)
        # Decode and verify token
        payload = decode_jwt(token)
        if not payload:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)

        # Attach the user object to the request
        try:
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        return view_func(request, *args, **kwargs)

    return wrapper
