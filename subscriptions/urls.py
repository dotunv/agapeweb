from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Plans
    path('plans/', views.PlanListView.as_view(), name='plan_list'),
    path('plans/<int:pk>/', views.PlanDetailView.as_view(), name='plan_detail'),
    path('plans/<int:plan_id>/subscribe/', views.subscribe, name='subscribe'),
    
    # Subscriptions
    path('my-subscription/', views.my_subscription, name='my_subscription'),
    path('queue-status/', views.queue_status, name='queue_status'),
    
    # Contributions
    path('contributions/', views.ContributionListView.as_view(), name='contribution_list'),
    
    # Wallet
    path('wallet/', views.wallet_overview, name='wallet_overview'),
    
    # Referrals
    path('referrals/', views.referral_overview, name='referral_overview'),
]
