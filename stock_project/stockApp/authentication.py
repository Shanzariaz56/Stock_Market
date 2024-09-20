import jwt
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
    
""" Decorator that ensures JWT token is valid and attaches the user to the request.
"""
"""def jwt_required(func):
    def wrapper(request, *args,**kwargs):
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
        return func(request, *args, **kwargs)
    
    return wrapper"""
def jwt_required(func):
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
    
    return wrapper
