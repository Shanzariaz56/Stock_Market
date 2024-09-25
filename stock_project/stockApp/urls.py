from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include

# Registering the viewsets with DefaultRouter
router = DefaultRouter()
router.register(r'register', RegisterView, basename='register')
router.register(r'login', LoginView, basename='login')
router.register(r'user', UserView, basename='user')
router.register(r'stock', StockView, basename='stock')
router.register(r'transaction', TransactionView, basename='transaction')

# URL patterns
urlpatterns = [
    # Include router-generated URLs
    path('', include(router.urls)),
    
    # Additional custom paths for transactions
    path('transaction/<int:user_id>/', TransactionView.as_view({'get': 'list'}), name='transaction-list'),
    
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # User Views
    path('user/', userListView.as_view(), name='user-list'),
    path('user/create/', userCreateView.as_view(), name='user-create'),
    path('user/<str:username>/', UserDetailView.as_view(), name='user-detail'),
    path('user/id/<int:id>/', userByIdView.as_view(), name='user-detail-id'),
    
    # Stock Views
    path('stocks/create/', StockCreateView.as_view(), name='stock-create'),
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/<str:ticker>/', StockByTickerView.as_view(), name='stock-ticker'),
    path('stocks/id/<int:pk>/', StockByIdView.as_view(), name='stock-detail'),

    # Transaction Views
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('transactions/<str:username>/<str:start_time>/<str:end_time>/', TransactionsByDateView.as_view(), name='transactions-by-date'),
]
