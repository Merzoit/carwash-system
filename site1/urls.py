"""site1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.http import JsonResponse

def health_check(request):
    import os
    return JsonResponse({
        'status': 'ok',
        'timestamp': '2025-12-28',
        'port': os.getenv('PORT', '8000'),
        'debug': os.getenv('DEBUG', 'False')
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('', include('authentication.urls')),
    path('', include('carwash.urls')),
    path('', include('warehouse.urls')),
    path('', include('accounting.urls')),
    path('', include('change_requests.urls')),
    path('', include('system_settings.urls')),
    path('', include('dashboard.urls')),
]
