from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, WithdrawalViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'withdrawals', WithdrawalViewSet, basename='withdrawal')

urlpatterns = [
    path('', include(router.urls)),
] 