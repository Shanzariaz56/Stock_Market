from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.views import APIView
from .models import Stock, Transaction, user
from .serializers import userSerializer, stockSerializer, transactionSerializer, registerSerializer
from django.utils.dateparse import parse_datetime
from .authentication import user_authentication, jwt_required
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from decimal import Decimal


# Create CB views here.
''' Register View'''

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=registerSerializer)
    def post(self, request):
        serializer = registerSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)

            user = User.objects.create(username=username, password=make_password(password))
            return JsonResponse({"message": "User registered successfully"}, status=201)

        return JsonResponse({"error": serializer.errors}, status=400)  # Corrected indentation


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=registerSerializer)
    def post(self, request):
        ''' 
             Login View (LOGIN ALREADY EXISTING USER)
        here is LOGIN VIEW that will take the user data like username and password 
        and use built in user in it and get data
        '''
        username = request.data.get("username")
        password = request.data.get("password")
        token = user_authentication(username, password)
        if token:
            return Response({'token': token}, status=200)
        else:
            return Response({"error": "Invalid credentials"}, status=400)


'''
      USER VIEW
'''
class userListView(APIView):
    @method_decorator(jwt_required)
    def get(self,request):
        '''
        GET ALL USER
        get record of all the user from database
        '''
        users=user.objects.all()
        serializer=userSerializer(users,many=True)
        return Response(serializer.data)
    
class userCreateView(APIView):
    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=userSerializer)
    def post(self,request):
        """
        Create a new user.
        This method receives user data through a POST request and attempts 
        to create a new user in the database,
        It validates the input data using the userSerializer and, if valid, saves the new user.
        
        """
        serializer = userSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class UserDetailView(APIView):
    @method_decorator(jwt_required)
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('username', openapi.IN_PATH, description='Username of the user', type=openapi.TYPE_STRING)]
    )
    def get(self, request, username=None):
        '''
             Get specific record 
        first send username as a request and 
        then match with already existing username in database
        and then apply serialization and return Response
        '''
        if username:
            users = get_object_or_404(user, username=username)
            serializer = userSerializer(users)
            return Response(serializer.data)
        users = user.objects.all()
        serializer = userSerializer(users, many=True)
        return Response(serializer.data)
   
class userByIdView(APIView):
    @method_decorator(jwt_required)
    def get(self,request,id):
        '''
             Retrive Specific record BY ID.
        This endpoint allows authenticated users to retrieve detailed information
        about a specific stock identified by its unique ID (primary key)
        '''
        users = get_object_or_404(user, id=id)
        serializer = userSerializer(users)
        return Response(serializer.data) 

'''    STOCK VIEW  '''

class StockCreateView(APIView):
    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=stockSerializer)
    def post(self,request):
        '''  
               CREATE NEW STOCK
        First make a create function that can add stock data 
        send request and then apply serialization 
        after that check validation and save data/serializer
        return Reponse
        '''
        serializer=stockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
        
class StockListView(APIView):
    @method_decorator(jwt_required)
    def get(self,request):
    
        ''' Now GET viw to retrieve all Stock data
        first send request, then apply serialization 
        return Response
        '''
        stock=Stock.objects.all()
        serializer=stockSerializer(stock,many=True)
        return Response(serializer.data)

class StockByTickerView(APIView):
    @method_decorator(jwt_required)
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('ticker', openapi.IN_PATH, description='Ticker symbol of the stock', type=openapi.TYPE_STRING, required=True)])
    def get(self,request,ticker):
        
        ''' Now GET view to retrieve specific Stock data based on ticker
        and ticker is a symbol that is unique so, send request with ticker
        check if match apply serialization and then return Response
        '''
        stock=get_object_or_404(Stock,ticker=ticker)
        serializer=stockSerializer(stock,many=False)
        return Response(serializer.data)

class StockByIdView(APIView):
    @method_decorator(jwt_required)
    def get(self, request, pk=None):
        '''
        Retrieve a specific stock by its ID.
        This endpoint allows authenticated users to retrieve detailed information
        about a specific stock identified by its unique ID (primary key)
        '''
        stock = get_object_or_404(Stock, id=pk)
        serializer = stockSerializer(stock)
        return Response(serializer.data)

''' TRANSACTION VIEW'''

class TransactionListView(APIView):
    @method_decorator(jwt_required)
    def get(self, request):
        ''' Now GET viw to retrieve all transaction data
        first send request, then apply serialization 
        return Response
        '''
        transactions = Transaction.objects.all()
        serializer = transactionSerializer(transactions, many=True)
        return Response(serializer.data)

class TransactionCreateView(APIView):
    @method_decorator(jwt_required)
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
            'ticker': openapi.Schema(type=openapi.TYPE_INTEGER, description='Ticker symbol of the stock'),
            'transaction_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['Buy', 'Sell'], description='Type of transaction'),
            'transaction_volume': openapi.Schema(type=openapi.TYPE_INTEGER, description='Volume of shares to transact'),
        },
        required=['user_id', 'ticker', 'transaction_type', 'transaction_volume'],
    ))
    def post(self, request):
        '''To post a new transaction. This should take user_id, ticker, transaction_type, and transaction_volume, 
        calculate the transaction_price based on the current stock price and transaction_volume,
        then apply validation on user balance and update the user's balance.
        '''
        user_id = request.data.get('user_id')
        ticker = request.data.get('ticker')
        transaction_type = request.data.get('transaction_type')
        transaction_volume = request.data.get('transaction_volume')

        if user_id is None or ticker is None:
            return Response({"error": "User ID and ticker are required."}, status=400)

        try:
            user_instance = user.objects.get(pk=user_id) 
            stock_instance = Stock.objects.get(pk=ticker)  
        except user.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)

        transaction_volume = int(request.data.get('transaction_volume'))
        transaction_price = stock_instance.price * Decimal(transaction_volume) 
        if transaction_type == "Buy":
            if user_instance.Initial_balance < transaction_price:
                return Response({"message": "Insufficient Balance"}, status=status.HTTP_400_BAD_REQUEST)
            user_instance.Initial_balance -= transaction_price  
        else:
            user_instance.Initial_balance += transaction_price

        user_instance.save()

        transaction = Transaction.objects.create(
            user_id=user_instance, 
            ticker=stock_instance,   
            transaction_type=transaction_type,
            transaction_volume=transaction_volume,
            transaction_price=transaction_price,
        )
        serializer = transactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TransactionsByDateView(APIView):

    @method_decorator(jwt_required)
    @swagger_auto_schema()
    def get(self, request, username, start_time, end_time):
        
        """
        View transactions created by the user in a certain period using the `GET` method.
        
        @param request: The request object containing user inputted data
        @param username: The username of the user
        @param start_time: The starting time of the transaction (YYYY-MM-DD)
        @param end_time: The ending time of the transaction (YYYY-MM-DD)
        """
        try:
            start_date = datetime.strptime(start_time, '%Y-%m-%d')
            end_date = datetime.strptime(end_time, '%Y-%m-%d')

            user_instance = user.objects.get(username=username)
            transactions = Transaction.objects.filter(
                user_id=user_instance, 
                time__date__gte=start_date,
                time__date__lte=end_date
            )
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except user.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

