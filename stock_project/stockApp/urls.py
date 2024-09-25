from django.urls import path
from .views import *

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # User Views
    path('user/', userListView.as_view(), name='user-list'),
    path('user/create/', userCreateView.as_view(), name='user'),
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
    #path('transactions/<str:username>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/<str:username>/<str:start_time>/<str:end_time>/',TransactionsByDateView.as_view(), name='transactions-by-date'),
]
