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
from frontend import admin_urls

urlpatterns = [
    # Frontend URLs
    path('', include('frontend.urls', namespace='frontend')),
    
    # Custom Admin Panel
    path('admin/', include((admin_urls.urlpatterns, 'admin'), namespace='admin')),
    
    # Django Admin (optional, you can remove if not needed)
    path('django-admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/', include('allauth.urls')),
    
    # App URLs
    path('users/', include('users.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('transactions/', include('transactions.urls')),
    path('core/', include('core.urls')),
]

# Debug Toolbar URLs (must be before static/media URLs)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Static and Media files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
