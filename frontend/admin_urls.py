from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    path('login/', admin_views.admin_login, name='login'),
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('users/', admin_views.manage_users, name='manage_users'),
    path('users/create-staff/', admin_views.create_staff_user, name='create_staff_user'),
    path('users/search-suggestions/', admin_views.search_suggestions, name='search_suggestions'),
    path('withdrawals/', admin_views.manage_withdrawals, name='manage_withdrawals'),
    path('deposits/', admin_views.manage_deposits, name='manage_deposits'),
    path('user/<int:user_id>/balance/', admin_views.user_balance, name='user_balance'),
    path('withdrawal/<int:withdrawal_id>/process/', admin_views.process_withdrawal, name='process_withdrawal'),
]