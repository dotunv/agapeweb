from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    
    # Authentication
    path('register/', views.register, name='register'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/fund-account/', views.fund_account, name='fund_account'),
    path('dashboard/submit-payment/', views.submit_payment, name='submit_payment'),
    path('dashboard/plans/', views.plans, name='plans'),
    path('dashboard/subscriptions/', views.subscriptions, name='subscriptions'),
    path('dashboard/referrals/', views.referrals, name='referrals'),
    path('dashboard/notifications/', views.notifications, name='notifications'),
    path('dashboard/withdrawal/', views.withdrawal, name='withdrawal'),
    path('dashboard/profile/', views.profile, name='profile'),
] 