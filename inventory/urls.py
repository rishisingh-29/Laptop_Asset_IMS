# inventory/urls.py

from django.urls import path
from .views import (
    auth_views, 
    dashboard_views, 
    asset_views, 
    employee_views, 
    allocation_views, 
    log_views,
    api_views
)

app_name = 'inventory'

urlpatterns = [
    # --- Authentication Views ---
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),
    path('access-denied/', auth_views.access_denied_view, name='access_denied'),

    # --- Dashboard Views ---
    path('', dashboard_views.dashboard_redirect_view, name='dashboard'),

    # --- Asset Management Views ---
    path('assets/', asset_views.asset_list, name='asset_list'),
    path('assets/add/', asset_views.add_asset, name='add_asset'),
    # NEW: URLs for editing and deleting assets
    path('assets/<str:pk>/edit/', asset_views.add_asset, name='edit_asset'),
    path('assets/<str:pk>/delete/', asset_views.delete_asset, name='delete_asset'),

    # --- Employee Management Views ---
    path('employees/', employee_views.employee_list, name='employee_list'),
    path('employees/add/', employee_views.add_employee, name='add_employee'),
    # NEW: URLs for editing and deleting employees
    path('employees/<int:pk>/edit/', employee_views.add_employee, name='edit_employee'),
    path('employees/<int:pk>/delete/', employee_views.delete_employee, name='delete_employee'),

    # --- Allocation & Transaction Views ---
    path('allocations/', allocation_views.allocation_list, name='allocation_list'),
    path('allocate/', allocation_views.allocation_form, name='allocation_form'),
    path('transactions/search/', allocation_views.transaction_search, name='transaction_search'),

    # --- Audit Log Viewer ---
    path('logs/', log_views.audit_log_viewer, name='audit_log_viewer'),

    # ===================================================================
    # API VIEWS
    # ===================================================================
    path('api/asset-details/<str:asset_id>/', api_views.get_asset_details, name='ajax_get_asset_details'),
    path('api/employee-assets/', api_views.get_employee_assets, name='ajax_get_employee_assets'),
    path('api/asset-history/<str:asset_id>/', api_views.get_asset_history, name='get_asset_history'),
    # NEW: API URLs for the confirmation modals
    path('api/detailed-asset/<str:asset_id>/', api_views.get_detailed_asset_info, name='get_detailed_asset_info'),
    path('api/detailed-employee/<int:employee_id>/', api_views.get_detailed_employee_info, name='get_detailed_employee_info'),
]