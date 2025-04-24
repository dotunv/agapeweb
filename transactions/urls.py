from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Transactions
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Withdrawals
    path('withdrawals/', views.WithdrawalListView.as_view(), name='withdrawal_list'),
    path('withdrawals/new/', views.WithdrawalCreateView.as_view(), name='withdrawal_create'),
    path('withdrawals/<int:pk>/approve/', views.approve_withdrawal, name='withdrawal_approve'),
    path('withdrawals/<int:pk>/reject/', views.reject_withdrawal, name='withdrawal_reject'),
] 