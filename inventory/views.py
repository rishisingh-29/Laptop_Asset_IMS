from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Asset, Allocation
from .forms import AllocationForm, ReturnForm
from django.db.models import Q

from django.db.models import Count

from django.shortcuts import render
from .models import Employee, Asset
from django.db.models import Count
from django.utils import timezone

def home(request):
    total_employees = Employee.objects.filter(status='active').count()
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(status='allocated').count()
    unassigned_assets = Asset.objects.filter(status='available').count()
    health_check_assets = Asset.objects.filter(status='under repair').count()

    employees = Employee.objects.all()

    # Pie Chart (status-wise count)
    status_counts = Asset.objects.values('status').annotate(count=Count('id'))

    # Stacked Bar Chart: overall in stock vs in production (allocated)
    instock_count = Asset.objects.filter(status='available').count()
    inproduction_count = Asset.objects.filter(status='allocated').count()

    context = {
        'total_employees': total_employees,
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
        'unassigned_assets': unassigned_assets,
        'health_check_assets': health_check_assets,
        'employees': employees,
        'status_counts': list(status_counts),
        'instock_count': instock_count,
        'inproduction_count': inproduction_count,
    }
    return render(request, 'inventory/home.html', context)

def employee_list(request):
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    employees = Employee.objects.all()

    if query:
        employees = employees.filter(
            Q(full_name__icontains=query) | Q(email__icontains=query)
        )

    if status_filter in ['active', 'inactive']:
        employees = employees.filter(status=status_filter)

    return render(request, 'inventory/employee_list.html', {
        'employees': employees,
        'query': query,
        'status_filter': status_filter,
    })

def asset_list(request):
    assets = Asset.objects.all()

    # Status chart
    status_counts = Asset.objects.values('status').annotate(count=Count('id'))

    # In stock vs in production counts
    instock_count = Asset.objects.filter(status='available').count()
    inproduction_count = Asset.objects.filter(status='allocated').count()

    return render(request, 'inventory/asset_list.html', {
        'assets': assets,
        'status_counts': list(status_counts),
        'instock_count': instock_count,
        'inproduction_count': inproduction_count,
        'active_page': 'asset'  # ← mark this page as active
    })


def allocation_list(request):
    allocations = Allocation.objects.select_related('employee', 'asset')
    return render(request, 'inventory/allocation_list.html', {'allocations': allocations})

def allocate_asset(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'allocate':
            form = AllocationForm(request.POST)
            if form.is_valid():
                # 1. Get objects using custom form fields (employee_email, asset_id)
                employee_email = form.cleaned_data['employee_email']
                asset_serial_no = form.cleaned_data['asset_id'].serial_no 
                assigned_date = form.cleaned_data['assigned_date']
                
                # Look up the actual objects
                employee_obj = Employee.objects.get(email=employee_email)
                asset_obj = Asset.objects.get(serial_no=asset_serial_no)
                
                # Save the new Allocation record
                Allocation.objects.create(
                    employee=employee_obj,
                    asset=asset_obj,
                    type='New', # Based on Allocation model choices
                    status='Allocated', # Based on Allocation model choices
                    reason=form.cleaned_data['requirement_reason'],
                    assigned_date=assigned_date,
                    # We can log other custom fields here if we created a separate model for asset condition tracking
                )
                
                # Update the Asset status to 'allocated'
                asset_obj.status = 'allocated'
                asset_obj.save()
                
                return redirect('allocation_list')
        
        elif form_type == 'return':
            form = ReturnForm(request.POST)
            if form.is_valid():
                # 1. Get objects using custom form fields
                asset_serial_no = form.cleaned_data['asset_id'].serial_no
                returned_date = form.cleaned_data['return_date']
                return_reason = form.cleaned_data['return_reason']
                
                # Look up the actual objects
                asset_obj = Asset.objects.get(serial_no=asset_serial_no)
                
                # Find the *current* allocation record for this asset
                try:
                    current_allocation = Allocation.objects.get(
                        asset=asset_obj, 
                        status='Allocated' # Find the active allocation
                    )
                except Allocation.DoesNotExist:
                    # Should be caught by form clean, but good to handle here
                    return redirect('allocation_list')

                # Update the existing Allocation record to mark it as returned
                current_allocation.status = 'Returned'
                current_allocation.type = 'Return'
                current_allocation.returned_date = returned_date
                current_allocation.reason = f"Return Reason: {return_reason}. Original Reason: {current_allocation.reason}"
                current_allocation.save()

                # Update the Asset status back to 'available'
                asset_obj.status = 'available'
                asset_obj.save()
                
                return redirect('allocation_list')
        
        # If the form was invalid, it falls through to the render part below
        else:
            # Re-instantiate the forms, ensuring only the submitted form has errors
            allocate_form = AllocationForm(request.POST if form_type == 'allocate' else None)
            return_form = ReturnForm(request.POST if form_type == 'return' else None)
            
    else:
        # GET request: instantiate empty forms
        allocate_form = AllocationForm(initial={'assigned_date': timezone.now().strftime('%Y-%m-%d')})
        return_form = ReturnForm(initial={'return_date': timezone.now().strftime('%Y-%m-%d')})
        
    context = {
        'allocation_form': allocate_form, 
        'return_form': return_form
    }
    return render(request, 'inventory/allocation_form.html', context)