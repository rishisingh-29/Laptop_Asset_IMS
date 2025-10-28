# inventory/views/dashboard_views.py

from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required
import json

from ..models import Employee, Asset, Allocation, AuditLog
from ..decorators import role_required

@login_required
def dashboard_redirect_view(request):
    """
    Acts as a router to redirect users to the correct dashboard based on their role.
    This is the main entry point after login.
    """
    user = request.user
    
    if user.is_superuser or user.groups.filter(name='IT_Admin').exists():
        return admin_dashboard(request)
    elif user.groups.filter(name='Employee').exists():
        return employee_dashboard(request)
    else:
        # Fallback for users with no role - show a restricted page.
        return employee_dashboard(request)

# Note: The @login_required is not strictly needed here because dashboard_redirect_view already has it,
# but it's good practice for clarity and security if these views were ever called directly.
@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def admin_dashboard(request):
    """Displays the comprehensive dashboard for IT Admins and Super Admins."""
    total_employees = Employee.objects.filter(status='Active').count()
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(status='Allocated').count()
    available_assets = Asset.objects.filter(status='Available').count()
    
    status_counts = list(Asset.objects.values('status').annotate(count=Count('status')))
    
    bar_chart_data = {
        'labels': [item['status'] for item in status_counts],
        'data': [item['count'] for item in status_counts],
    }

    recent_logs = AuditLog.objects.select_related('actor').order_by('-timestamp')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
        'available_assets': available_assets,
        'status_counts_json': json.dumps(status_counts),
        'bar_chart_data_json': json.dumps(bar_chart_data),
        'recent_logs': recent_logs,
    }
    return render(request, 'inventory/dashboards/admin_dashboard.html', context)

@login_required
@role_required(allowed_roles=['Employee'])
def employee_dashboard(request):
    """Displays the simplified dashboard for standard employees."""
    try:
        employee = request.user.employee_profile
        assigned_allocations = Allocation.objects.filter(
            employee=employee,
            transaction_status='Allocated'
        ).select_related('asset').order_by('-assigned_date')
    except Employee.DoesNotExist:
        assigned_allocations = []

    context = {
        'assigned_allocations': assigned_allocations,
    }
    return render(request, 'inventory/dashboards/employee_dashboard.html', context)