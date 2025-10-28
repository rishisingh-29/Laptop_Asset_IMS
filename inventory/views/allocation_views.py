# inventory/views/allocation_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from ..models import Employee, Asset, Allocation
from ..forms import AllocationForm, ReturnForm
from ..decorators import role_required

@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def allocation_list(request):
    """
    Displays a paginated list of all historical and active allocations.
    """
    # Eager load related employee and asset objects to prevent N+1 queries.
    allocations_queryset = Allocation.objects.select_related('employee', 'asset').order_by('-assigned_date')

    # Pagination
    paginator = Paginator(allocations_queryset, 15) # Show 15 allocations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'inventory/allocations/allocation_list.html', context)


@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def allocation_form(request):
    """
    Handles the dual-purpose form for both assigning a new asset and
    processing the return of an existing asset.
    """
    # Initialize forms for the GET request or in case of errors
    assign_form = AllocationForm()
    return_form = ReturnForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # --- Logic for Assigning an Asset ---
        if form_type == 'assign':
            assign_form = AllocationForm(request.POST)
            if assign_form.is_valid():
                try:
                    # Find the employee by the provided email
                    employee = Employee.objects.get(email=assign_form.cleaned_data['employee_email'])
                    
                    # Create the allocation record
                    allocation = assign_form.save(commit=False)
                    allocation.employee = employee
                    allocation.transaction_status = 'Allocated'
                    allocation.assigned_date = timezone.now() # Set assignment date automatically
                    allocation.save()
                    
                    # Update the asset's status to 'Allocated'
                    asset = assign_form.cleaned_data['asset']
                    asset.status = 'Allocated'
                    asset.save()
                    
                    messages.success(request, f"Asset '{asset.serial_number}' successfully assigned to {employee.full_name}.")
                    return redirect('inventory:allocation_list')
                
                # Validation: Handle case where employee does not exist
                except Employee.DoesNotExist:
                    assign_form.add_error('employee_email', 'Employee with this email does not exist.')

        # --- Logic for Returning an Asset ---
        elif form_type == 'return':
            return_form = ReturnForm(request.POST)
            
            # Dynamically populate the asset dropdown based on the employee email.
            # This is a security measure to ensure you can only return assets the employee actually has.
            if 'employee_email' in request.POST:
                try:
                    employee = Employee.objects.get(email=request.POST['employee_email'])
                    asset_ids = Allocation.objects.filter(employee=employee, transaction_status='Allocated').values_list('asset_id', flat=True)
                    return_form.fields['asset'].queryset = Asset.objects.filter(asset_id__in=asset_ids)
                except Employee.DoesNotExist:
                    pass # Let the form validation handle the "does not exist" error
            
            if return_form.is_valid():
                asset = return_form.cleaned_data['asset']
                employee = Employee.objects.get(email=return_form.cleaned_data['employee_email'])
                
                try:
                    # Find the specific active allocation to update
                    allocation_to_update = Allocation.objects.get(asset=asset, employee=employee, transaction_status='Allocated')
                    
                    # Update the found allocation record with data from the return form
                    for field_name, value in return_form.cleaned_data.items():
                        if hasattr(allocation_to_update, field_name):
                            setattr(allocation_to_update, field_name, value)
                    
                    allocation_to_update.returned_date = timezone.now() # Set return date automatically
                    allocation_to_update.transaction_status = 'Returned'
                    allocation_to_update.save()
                    
                    # Update the asset's status back to 'Available'
                    asset.status = 'Available'
                    asset.save()
                    
                    messages.success(request, f"Asset '{asset.serial_number}' successfully returned from {employee.full_name}.")
                    return redirect('inventory:allocation_list')

                # Validation: Handle case where the active allocation to return isn't found
                except Allocation.DoesNotExist:
                    return_form.add_error(None, "Could not find an active allocation for this asset and employee combination.")

    # Render the page with both forms
    context = {
        'assign_form': assign_form,
        'return_form': return_form
    }
    return render(request, 'inventory/allocations/allocation_form.html', context)


@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def transaction_search(request):
    """
    Provides a targeted search for all transactions related to a specific
    employee or asset ('Know Transaction' feature).
    """
    search_type = request.GET.get('search_type', 'employee')
    query = request.GET.get('query', '').strip()
    results = None
    
    if query:
        if search_type == 'employee':
            # Search by employee name or email
            results = Allocation.objects.filter(
                Q(employee__full_name__icontains=query) | 
                Q(employee__email__icontains=query)
            ).select_related('employee', 'asset').order_by('-assigned_date')
        
        elif search_type == 'asset':
            # Search by asset serial number or ID
            results = Allocation.objects.filter(
                Q(asset__serial_number__icontains=query) | 
                Q(asset__asset_id__icontains=query)
            ).select_related('employee', 'asset').order_by('-assigned_date')
    
    context = {
        'search_type': search_type,
        'query': query,
        'results': results,
    }
    return render(request, 'inventory/allocations/transaction_search.html', context)