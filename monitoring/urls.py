from django.urls import path
from . import views

urlpatterns = [
    path('test-sentry/', views.test_sentry, name='test-sentry'),
    path('test-user-context/', views.test_user_context, name='test-user-context'),
    path('test-performance/', views.test_performance, name='test-performance'),
] 