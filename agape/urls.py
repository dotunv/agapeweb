"""
URL configuration for agape project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from knox.views import LogoutView, LogoutAllView
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django_prometheus import exports

from agape.admin import admin_site

def redirect_to_docs(request):
    return redirect('swagger-ui')

urlpatterns = [
    path('', redirect_to_docs, name='home'),
    path('admin/', admin_site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Monitoring
    path('metrics/', exports.ExportToDjangoView, name='prometheus-django-metrics'),
    
    # API Routes
    path('api/auth/', include('knox.urls')),
    path('api/auth/logout/', LogoutView.as_view(), name='knox_logout'),
    path('api/auth/logoutall/', LogoutAllView.as_view(), name='knox_logoutall'),
    path('api/users/', include('users.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/transactions/', include('transactions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
