from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.SubscriptionPlanViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register(r'contributions', views.ContributionViewSet, basename='contribution')
router.register(r'queues', views.QueueViewSet, basename='queue')
router.register(r'wallets', views.WalletViewSet, basename='wallet')
router.register(r'referrals', views.ReferralViewSet, basename='referral')

urlpatterns = [
    path('', include(router.urls)),
]
