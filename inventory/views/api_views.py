# inventory/views/api_views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime

from ..models import Asset, Employee, Allocation
from ..decorators import role_required

@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def get_asset_details(request, asset_id):
    """
    API endpoint to fetch basic details for a given asset_id.
    Called by JavaScript in the allocation form.
    Returns a JSON response.
    """
    try:
        asset = Asset.objects.get(asset_id=asset_id)
        data = {
            'brand': asset.brand,
            'model': asset.model,
            'processor': asset.processor,
        }
        return JsonResponse(data)
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Asset not found'}, status=404)

@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def get_employee_assets(request):
    """
    API endpoint to find all currently allocated assets for a given employee email.
    Called by JavaScript in the return form.
    Returns a JSON list of assets.
    """
    email = request.GET.get('email', '').strip()
    if not email:
        return JsonResponse({'error': 'Email parameter is required'}, status=400)
    
    try:
        employee = Employee.objects.get(email__iexact=email)
        allocations = Allocation.objects.filter(
            employee=employee, 
            transaction_status='Allocated'
        ).select_related('asset')
        
        assets = [{
            'id': alloc.asset.asset_id, 
            'text': f"{alloc.asset.brand} {alloc.asset.model}",
            'serial': alloc.asset.serial_number
        } for alloc in allocations]
        
        return JsonResponse({'assets': assets})
    except Employee.DoesNotExist:
        return JsonResponse({'assets': []})

@login_required
def get_asset_history(request, asset_id):
    """
    API endpoint to fetch the full transaction history for a specific asset.
    Called by the employee dashboard.
    Returns a JSON list of allocation records.
    """
    try:
        asset = Asset.objects.get(asset_id=asset_id)
        user = request.user

        is_admin = user.is_superuser or user.groups.filter(name__in=['IT_Admin', 'Super_Admin']).exists()
        is_current_owner = Allocation.objects.filter(
            asset=asset, 
            employee__user=user, 
            transaction_status='Allocated'
        ).exists()

        if not is_admin and not is_current_owner:
            return JsonResponse({'error': 'You do not have permission to view this asset\'s history.'}, status=403)

        history = Allocation.objects.filter(
            asset=asset
        ).select_related('employee').order_by('-assigned_date')
        
        history_data = list(history.values(
            'employee__full_name', 
            'assigned_date', 
            'returned_date'
        ))
        
        return JsonResponse({'history': history_data})
        
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Asset not found'}, status=404)

# ===================================================================
# NEW: API View for Asset Deletion Modal
# ===================================================================
@login_required
@role_required(allowed_roles=['Super_Admin'])
def get_detailed_asset_info(request, asset_id):
    """
    Fetches comprehensive details about an asset for the delete confirmation modal.
    """
    try:
        asset = Asset.objects.select_related().get(asset_id=asset_id)
        
        # Get current allocation info
        current_allocation = Allocation.objects.filter(asset=asset, transaction_status='Allocated').select_related('employee').first()
        
        # Get full transaction history
        history = Allocation.objects.filter(asset=asset).select_related('employee').order_by('-assigned_date')
        history_data = []
        for alloc in history:
            history_data.append({
                'employee_name': alloc.employee.full_name,
                'assigned_date': alloc.assigned_date.strftime('%b %d, %Y, %I:%M %p') if alloc.assigned_date else 'N/A',
                'returned_date': alloc.returned_date.strftime('%b %d, %Y, %I:%M %p') if alloc.returned_date else 'Currently Assigned'
            })

        data = {
            'asset_id': asset.asset_id,
            'serial_number': asset.serial_number,
            'brand': asset.brand,
            'model': asset.model,
            'status': asset.status,
            'purchase_date': asset.purchase_date.strftime('%B %d, %Y') if asset.purchase_date else 'N/A',
            'current_owner': current_allocation.employee.full_name if current_allocation else 'None (Available)',
            'history': history_data
        }
        return JsonResponse(data)
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Asset not found'}, status=404)

# ===================================================================
# NEW: API View for Employee Deletion Modal
# ===================================================================
@login_required
@role_required(allowed_roles=['Super_Admin'])
def get_detailed_employee_info(request, employee_id):
    """
    Fetches comprehensive details about an employee for the delete confirmation modal.
    """
    try:
        employee = Employee.objects.get(pk=employee_id)
        
        # Get all currently assigned assets
        assigned_assets = Allocation.objects.filter(employee=employee, transaction_status='Allocated').select_related('asset')
        assets_data = []
        for alloc in assigned_assets:
            assets_data.append({
                'brand': alloc.asset.brand,
                'model': alloc.asset.model,
                'serial_number': alloc.asset.serial_number,
                'assigned_date': alloc.assigned_date.strftime('%b %d, %Y')
            })
            
        data = {
            'employee_id': employee.employee_id,
            'full_name': employee.full_name,
            'email': employee.email,
            'designation': employee.designation,
            'status': employee.status,
            'assigned_assets': assets_data
        }
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)