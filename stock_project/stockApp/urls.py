from django.urls import path
from .views import *

urlpatterns = [
    path("add/users/",addUser),
    path("get/users/<str:username>",getUser),
    path("get/stocks/",getStock),
    path("add/stocks/",addStock),
    path("get/stocks/<str:ticker>",getStockbyTicker),
    path("add/transactions/",createTransaction),
    path("get/transactions/<int:user_id>",getTransactionbyId),
    path("get/transactions/<int:user_id>/<str:start_timestamp>/<str:end_timestamp>/", getTransactionByDate),
    path('auth/login/', login_user, name='user_login'),
    path('auth/register/', register, name='register'),

]
