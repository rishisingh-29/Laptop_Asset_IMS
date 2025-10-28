# asset_mgmt/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # The Django admin interface, a powerful tool for superusers.
    path('admin/', admin.site.urls),
    
    # This is the main entry point for your application.
    # It includes all URLs from `inventory.urls` under the `inventory` namespace.
    # This allows you to use `{% url 'inventory:asset_list' %}` in your templates.
    path('', include('inventory.urls')),
]