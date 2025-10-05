from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('employees/', views.employee_list, name='employee_list'),
    path('assets/', views.asset_list, name='asset_list'),
    path('allocations/', views.allocation_list, name='allocation_list'),
    path('allocate/', views.allocate_asset, name='allocation_form'),
    path('transactions/', views.transaction_search, name='transaction_search'),
    path('ajax/get_asset_details/', views.get_asset_details, name='ajax_get_asset_details'),
    path('ajax/get_employee_assets/', views.get_employee_assets, name='ajax_get_employee_assets'),
    path('assets/add/', views.add_asset, name='add_asset'), 
    path('employees/add/', views.add_employee, name='add_employee'),


]
