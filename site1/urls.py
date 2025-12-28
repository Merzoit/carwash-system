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
    import logging
    logger = logging.getLogger(__name__)

    port = os.getenv('PORT', '8000')
    response_data = {
        'status': 'ok',
        'timestamp': '2025-12-28',
        'port': port,
        'debug': os.getenv('DEBUG', 'False'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
        'remote_addr': request.META.get('REMOTE_ADDR', 'Unknown')
    }

    logger.info(f"Healthcheck called: port={port}, remote_addr={response_data['remote_addr']}")
    return JsonResponse(response_data)

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
