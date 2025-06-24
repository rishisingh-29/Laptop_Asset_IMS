from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('employees/', views.employee_list, name='employee_list'),
    path('assets/', views.asset_list, name='asset_list'),
    path('allocations/', views.allocation_list, name='allocation_list'),
    path('allocate/', views.allocate_asset, name='allocate_asset'),
]
