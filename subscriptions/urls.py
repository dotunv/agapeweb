from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'plans', views.PlanViewSet)
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscription')
router.register(r'contributions', views.ContributionViewSet, basename='contribution')
router.register(r'withdrawals', views.WithdrawalViewSet, basename='withdrawal')

urlpatterns = [
    path('', include(router.urls)),
] 