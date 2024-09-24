from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path, include


router=DefaultRouter()
router.register(r'register',RegisterView,basename='register')
router.register(r"login",LoginView,basename='login')
router.register(r'user',UserView,basename='user')
router.register(r'stock',StockView,basename='stock')
router.register(r'transaction',TransactionView,basename='transaction')
urlpatterns = [
    path('', include(router.urls)),
    path('transaction/<int:user_id>/', TransactionView.as_view({'get': 'list'}), name='transaction-list'),
]
