from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Transactions
    path('list/', views.TransactionListView.as_view(), name='transaction-list'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    
    # Withdrawals
    path('withdrawals/', views.WithdrawalListView.as_view(), name='withdrawal_list'),
    path('withdrawals/new/', views.WithdrawalCreateView.as_view(), name='withdrawal_create'),
    path('withdrawals/<int:pk>/approve/', views.approve_withdrawal, name='withdrawal_approve'),
    path('withdrawals/<int:pk>/reject/', views.reject_withdrawal, name='reject_withdrawal'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
] 