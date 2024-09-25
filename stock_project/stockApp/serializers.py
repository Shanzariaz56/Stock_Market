from rest_framework import serializers
from .models import *

''' first you may have to make a serializer for user'''
class userSerializer(serializers.ModelSerializer):
    class Meta:
        model=user
        fields=['username','Initial_balance']
        
''' Serializer for Stock and add all the fields'''
class stockSerializer(serializers.ModelSerializer):
    class Meta:
        model=Stock
        fields=['ticker','price']
        
''' serializer for Transaction and also include all fields in it '''
class transactionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Transaction
        fields=['user_id','ticker','transaction_type','transaction_volume','transaction_price','time']
        
''' Register Serializer that will be created to take a parameter in swagger body'''
class registerSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

