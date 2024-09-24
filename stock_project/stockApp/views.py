from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from .models import * 
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from .serializers import userSerializer,stockSerializer,transactionSerializer,registerSerializer
from django.utils.dateparse import parse_datetime
from .authentication import user_authentication, jwt_required
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse
from rest_framework.decorators import action
from .swagger import schema_view
from django.utils.decorators import method_decorator


# Create CB views here.
''' Register View'''

class RegisterView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=registerSerializer)
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = registerSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)

            user = User.objects.create(username=username, password=make_password(password))
            return JsonResponse({"message": "User registered successfully"}, status=201)

        return JsonResponse({"error": serializer.errors}, status=400)  # Corrected indentation



''' here is LOGIN VIEW that will take the user data like username and password 
and use built in user in it and get data'''

class LoginView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=registerSerializer)
    @action(detail=False, methods=['post'])
    def login_user(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        token = user_authentication(username, password)
        if token:
            return Response({'token': token}, status=200)
        else:
            return Response({"error": "Invalid credentials"}, status=400)


''' First we will make CB Vews for the user that first one is to post and other one is for get
To register a new user with a username and initial balance (POST Api)
To retrieve specific user data (GET Api)
'''
class UserView(viewsets.ModelViewSet):
    serializer=userSerializer
    
    ''' That will get all record from the database'''
    def get_queryset(self):
        return User.objects.all()

    '''Get specific record first send username as a request and 
    then match with already existing username in database
    and then apply serialization and return Response
    '''
    @swagger_auto_schema(method='get') 
    @method_decorator(jwt_required)
    def retrieve(self,request,username=None):
        user=get_object_or_404(User,username=username)
        serializer=userSerializer(user)
        return Response(serializer.data)
    
    """
    Create a new user.

    This method receives user data through a POST request and attempts 
    to create a new user in the database,
    It validates the input data 
    using the userSerializer and, if valid, saves the new user."""

    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=userSerializer)
    def create(self,request):
        serializer = userSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400) 

''' STOCK VIEW
To add stock data
To retrieve all stock data.
To retrieve specific stock data
'''

class StockView(viewsets.ModelViewSet):
    serializer_class=stockSerializer
    
    def get_queryset(self):
        return Stock.objects.all()
    
    
    ''' First make a create function that can add stock data 
    send request and then apply serialization 
    after that check validation and save data/serializer
    return Reponse'''
    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=stockSerializer)
    def create(self,request):
        serializer=stockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)

    ''' Now GET viw to retrieve all Stock data
    first send request, then apply serialization 
    return Response'''

    @method_decorator(jwt_required)
    @swagger_auto_schema(method='get')
    def list(self,request):
        stock=Stock.objects.all()
        serializer=stockSerializer(stock,many=True)
        return Response(serializer.data)

    ''' Now GET view to retrieve specific Stock data based on ticker
    and ticker is a symbol that is unique so, send request with ticker
    check if match apply serialization and then return Response'''

    @method_decorator(jwt_required)
    @swagger_auto_schema(method='get')
    @action(detail=False, methods=['get'])
    def retrieve_by_ticker(self,request,ticker):
        stock=get_object_or_404(Stock,ticker=ticker)
        serializer=stockSerializer(stock,many=False)
        return Response(serializer.data)

''' TRANSACTION VIEW'''

class TransactionView(viewsets.ModelViewSet):
    
    '''To post a new transaction. This should take user_id, ticker, transaction_type, and transaction_volume, 
    calculate the transaction_price based on the current stock price and transaction_volumn
    then apply validation on user balance
    update the user's balance.
    '''
    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=transactionSerializer)
    @action(detail=False, methods=['post'])
    def createTransaction(self,request):
        id = request.data.get('id')
        ticker = request.data.get('ticker')
        if user_id is None or ticker is None:
            return Response({"error": "User ID and ticker are required."}, status=400)
        try:
            user = User.objects.get(pk=id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found."}, status=404)
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
            ticker=stock,
            transaction_type=transaction_type,
            transaction_volume=transaction_volume,
            transaction_price=transaction_price,
        )
        serializer=transactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    ''' here is GET view To retrieve all transactions of a specific user.
    first check user id and then apply filter on it and after that
    apply serialization and return Response'''

    @method_decorator(jwt_required)
    @swagger_auto_schema(method='get')
    def list(self,request,id=None):
        user = get_object_or_404(User, pk=id)
        transactions = Transaction.objects.filter(user=user)  
        serializer = transactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    ''' here is GET view To retrieve transactions of a specific user between two timestamps
    first send request with id and start and end time
    match with user id and the apply parse on start and end date
    apply filter on id and range of start and end date
    apply serialization and then return Response'''
    @method_decorator(jwt_required)
    @swagger_auto_schema(method='get')
    @action(detail=False, methods=['get'])
    def retrieve_byDate(self,request, id, start_timestamp, end_timestamp):
        user = get_object_or_404(User, pk=id)
        start_time = parse_datetime(start_timestamp)  
        end_time = parse_datetime(end_timestamp)      
        transactions = Transaction.objects.filter(user=user, time__range=(start_time, end_time))
        serializer = transactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)