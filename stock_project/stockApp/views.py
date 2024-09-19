from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .model import * 
from .serializers import userSerializer,stockSerializer,transactionSerializer


# Create your views here.
''' First we will make api_views for the user that first one is to post and other one is for get
To register a new user with a username and initial balance (POST Api)
To retrieve specific user data (GET Api)
'''
@api_view(['POST'])
def addUser(request):
    serializer=userSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.error,status=400)

'''Get specific record first send username as a request and 
then match with already existing username in database
and then apply serialization and return Response
'''
@api_view(['GET'])
def getUser(request,username):
    user=get_object_or_404(username=username)
    serializer=userSerializer(user,many=True)
    return Response(serializer.data)

''' STOCK VIEW
To add stock data
To retrieve all stock data.
To retrieve specific stock data
'''
''' First make a POST view that can add stock data 
send request and then apply serialization 
after that check validation and save data/serializer
return Reponse'''

@api_view(['POST'])
def addStock(request):
    serializer=stockSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=201)
    return Response(serializer.error,status=400)

''' Now GET viw to retrieve all Stock data
first send request, then apply serialization 
return Response'''

@api_view(['GET'])
def getStock(request):
    stock=Stock.objects.all()
    serializer=stockSerializer(stock,many=True)
    return Response(serializer.data)

''' Now GET view to retrieve specific Stock data based on ticker
and ticker is a symbol that is unique so, send request with ticker
check if match apply serialization and then return Response'''

@api_view(['GET'])
def getStockbyTicker(request,ticker):
    stock=get_object_or_404(Stock,ticker=ticker)
    serializer=stockSerializer(stock,many=False)
    return Response(serializer.data)

''' TRANSACTION VIEW
To post a new transaction. This should take user_id, ticker, transaction_type, and transaction_volume, 
calculate the transaction_price based on the current stock price and transaction_volumn
then apply validation on user balance
update the user's balance.
'''

@api_view(['POST'])
def createTransaction(request):
    user=User.objects.get(pk=request.data['id'])
    stock=Stock.objects.get(ticker=request.data['ticker'])
    transaction_type=request.data['transaction_type']
    transaction_volume=int(request.data['transaction_volume'])
    transaction_price=stock.price * transaction_volume
    
    if transaction_type=="Buy" and user.Initial_balance < transaction_price:
        return Response({"message":"InSufficient Balance"},status=status.HTTP_400_BAD_REQUEST)
    
    if transaction_type=='Buy':
        user.Initial_balance +=transaction_price
    else:
        user.Initial_balance -=transaction_price
    user.save()
    
    transaction=Transaction.objects.create(
        user=user,
        ticker=ticker,
        transaction_type=transaction_type,
        transaction_volume=transaction_volume,
        transaction_price=transaction_price,
    )
    serializer=transactionSerializer(transaction)
    return Response(serializer.data,status=status.HTTP_201_CREATE)
    
    