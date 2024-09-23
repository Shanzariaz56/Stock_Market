"""import jwt
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

''' first need to generate a JWT token and then encode that token
''' 
def generate_jwt_token(user):
    payload={
        "id":user.pk,
        "username":user.username,
        "exp":datetime.utcnow()+timedelta(minutes=360),
        "iat":datetime.utcnow()
    }
    token=jwt.encode(payload,settings.SIMPLE_JWT["SIGNING_KEY"],algorithm=settings.SIMPLE_JWT["ALGORITHM"])
    return token

''' Authenticate the user and then generate the token for it'''
def user_authentication(username,password):
    user=authenticate(username=username,password=password)
    if user is not None:
        token=generate_jwt_token(user)
        return token
    return None

''' Now decode the JWT token and returns the user if the token is valid'''
def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, settings.SIMPLE_JWT["SIGNING_KEY"], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
        user_id = payload.get('id')  # Get user ID from the payload
        user = User.objects.get(id=user_id)  # Fetch the user based on the ID
        return user
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.DecodeError:
        raise AuthenticationFailed("Invalid token")
    except User.DoesNotExist:
        raise AuthenticationFailed("User not found")
    
# Decorator that ensures JWT token is valid and attaches the user to the request.
# def jwt_required(func):
#def wrapper(request, *args,**kwargs):
       auth_header = request.headers.get('Authorization')
        print(auth_header)
        if not auth_header:
            raise AuthenticationFailed('Token is missing')
        try:
            token = auth_header.split(' ')[1]  # Expecting token in 'Bearer <token>' format
            user = decode_jwt_token(token)
            request.user = user
        except IndexError:
            raise AuthenticationFailed('Token is malformed')
        except AuthenticationFailed:
            raise AuthenticationFailed('Invalid or expired token')
        return func(request, *args, **kwargs)"""
   # return wrapper"""
"""def jwt_required(func):
    def wrapper(request, *args, **kwargs):
        # Extract the token from the query parameters
        token = request.GET.get('token')
        if not token:
            raise AuthenticationFailed('Token is missing')
        try:
            user = decode_jwt_token(token)
            request.user = user
        except AuthenticationFailed:
            raise AuthenticationFailed('Invalid or expired token')
        return func(request, *args, **kwargs)
    
    return wrapper"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User

# Define your secret key and algorithm
SECRET_KEY = settings.SECRET_KEY  # Use `settings.SECRET_KEY` in production.
ALGORITHM = 'HS256'

# Generate a JWT token
def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(minutes=360)  # Token expires in 1 hour
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
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            token = generate_jwt(user)
            return token
        else:
            return None
    except User.DoesNotExist:
        return None

# JWT decorator for protecting views
from functools import wraps

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

