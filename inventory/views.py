# inventory/views.py

from django.shortcuts import render, redirect
from .models import Employee, Asset, Allocation
from .forms import AllocationForm, ReturnForm
from django.db.models import Q, Count, Prefetch # Prefetch ko yahan import karein
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .forms import AssetForm, BulkAssetImportForm
from django.contrib import messages

def home(request):
    total_employees = Employee.objects.filter(status='Active').count()
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(status='Allocated').count()
    unassigned_assets = Asset.objects.filter(status='Available').count()
    health_check_assets = Asset.objects.filter(status='Under Repair').count()
    employees = Employee.objects.order_by('-date_of_joining')[:10]
    status_counts = Asset.objects.values('status').annotate(count=Count('asset_id'))
    instock_count = unassigned_assets
    inproduction_count = assigned_assets

    context = {
        'total_employees': total_employees, 'total_assets': total_assets,
        'assigned_assets': assigned_assets, 'unassigned_assets': unassigned_assets,
        'health_check_assets': health_check_assets, 'employees': employees,
        'status_counts': list(status_counts), 'instock_count': instock_count,
        'inproduction_count': inproduction_count,
    }
    return render(request, 'inventory/home.html', context)

# ===================================================================
# === UPDATED employee_list FUNCTION ================================
# ===================================================================
def employee_list(request):
    # Sirf 'Allocated' status waali transactions ko pre-fetch karne ke liye ek QuerySet banayein
    active_allocations_prefetch = Prefetch(
        'allocation_set',
        queryset=Allocation.objects.filter(transaction_status='Allocated').select_related('asset'),
        to_attr='active_allocations' # Is naam se hum template mein data access karenge
    )

    # Employee queryset ke saath is prefetch ko jod dein
    employee_queryset = Employee.objects.prefetch_related(active_allocations_prefetch).order_by('full_name')

    # Pagination logic
    paginator = Paginator(employee_queryset, 10)
    page_number = request.GET.get('page')
    employees_page = paginator.get_page(page_number)

    return render(request, 'inventory/employee_list.html', {'employees': employees_page})
# ===================================================================
# === END OF UPDATED FUNCTION =======================================
# ===================================================================

def asset_list(request):
    asset_queryset = Asset.objects.all().order_by('asset_id')
    paginator = Paginator(asset_queryset, 10)
    page_number = request.GET.get('page')
    assets_page = paginator.get_page(page_number)
    status_counts = Asset.objects.values('status').annotate(count=Count('asset_id'))
    instock_count = Asset.objects.filter(status='Available').count()
    inproduction_count = Asset.objects.filter(status='Allocated').count()

    context = {
        'assets': assets_page,
        'status_counts': list(status_counts),
        'instock_count': instock_count,
        'inproduction_count': inproduction_count,
    }
    return render(request, 'inventory/asset_list.html', context)

def allocation_list(request):
    allocations = Allocation.objects.select_related('employee', 'asset').order_by('-assigned_date')
    return render(request, 'inventory/allocation_list.html', {'allocations': allocations})

def allocate_asset(request):
    # ... (allocate_asset function jaisa pehle tha, waisa hi rahega) ...
    # ... (no changes needed here) ...
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'allocate':
            form = AllocationForm(request.POST)
            if form.is_valid():
                try:
                    employee = Employee.objects.get(email=form.cleaned_data['employee_email'])
                    asset = form.cleaned_data['asset']
                    allocation = form.save(commit=False)
                    allocation.employee = employee
                    allocation.transaction_status = 'Allocated'
                    allocation.save()
                    asset.status = 'Allocated'
                    asset.save()
                    return redirect('allocation_list')
                except Employee.DoesNotExist:
                    form.add_error('employee_email', 'This employee email does not exist.')
        
        elif form_type == 'return':
            form = ReturnForm(request.POST)
            if form.is_valid():
                asset = form.cleaned_data['asset']
                employee = Employee.objects.get(email=form.cleaned_data['employee_email'])
                allocation_to_update = Allocation.objects.get(asset=asset, employee=employee, transaction_status='Allocated')
                allocation_to_update.returned_date = form.cleaned_data['returned_date']
                allocation_to_update.return_reason = form.cleaned_data['return_reason']
                allocation_to_update.condition_on_return = form.cleaned_data['condition_on_return']
                allocation_to_update.charger_returned = form.cleaned_data['charger_returned']
                allocation_to_update.bag_returned = form.cleaned_data['bag_returned']
                allocation_to_update.delivery_type = form.cleaned_data['delivery_type'] 
                allocation_to_update.return_docket_id = form.cleaned_data['return_docket_id']
                allocation_to_update.transaction_status = 'Returned'
                allocation_to_update.save()
                asset.status = 'Available' 
                asset.save()
                return redirect('allocation_list')

    if request.method == 'POST' and request.POST.get('form_type') == 'allocate':
        allocate_form = AllocationForm(request.POST)
        return_form = ReturnForm()
    elif request.method == 'POST' and request.POST.get('form_type') == 'return':
        return_form = ReturnForm(request.POST)
        allocate_form = AllocationForm()
    else: 
        allocate_form = AllocationForm()
        return_form = ReturnForm()
            
    context = {
        'allocation_form': allocate_form, 
        'return_form': return_form
    }
    return render(request, 'inventory/allocation_form.html', context)


def transaction_search(request):
    search_type = request.GET.get('search_type', 'employee')
    query = request.GET.get('query', '')
    results = None
    if query:
        if search_type == 'employee':
            results = Allocation.objects.filter(
                Q(employee__full_name__icontains=query) | 
                Q(employee__email__icontains=query)
            ).select_related('employee', 'asset').order_by('-assigned_date')
        elif search_type == 'asset':
            results = Allocation.objects.filter(
                Q(asset__serial_number__icontains=query) | 
                Q(asset__asset_id__icontains=query)
            ).select_related('employee', 'asset').order_by('-assigned_date')
    context = {
        'search_type': search_type,
        'query': query,
        'results': results,
    }
    return render(request, 'inventory/transaction_search.html', context)

def allocate_asset(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'allocate':
            form = AllocationForm(request.POST)
            if form.is_valid():
                try:
                    employee = Employee.objects.get(email=form.cleaned_data['employee_email'])
                    allocation = form.save(commit=False)
                    allocation.employee = employee
                    allocation.transaction_status = 'Allocated'
                    # Manually save other fields not directly on the form model
                    allocation.delivery_type = form.cleaned_data['delivery_type']
                    allocation.save()
                    
                    asset = form.cleaned_data['asset']
                    asset.status = 'Allocated'
                    asset.save()
                    return redirect('allocation_list')
                except Employee.DoesNotExist:
                    form.add_error('employee_email', 'Employee with this email does not exist.')
        
        elif form_type == 'return':
            form = ReturnForm(request.POST)
            # Update the form's queryset dynamically before validation
            if 'employee_email' in request.POST:
                try:
                    employee = Employee.objects.get(email=request.POST['employee_email'])
                    active_allocations = Allocation.objects.filter(employee=employee, transaction_status='Allocated')
                    asset_ids = active_allocations.values_list('asset_id', flat=True)
                    form.fields['asset'].queryset = Asset.objects.filter(asset_id__in=asset_ids)
                except Employee.DoesNotExist:
                    pass
            
            if form.is_valid():
                asset = form.cleaned_data['asset']
                employee = Employee.objects.get(email=form.cleaned_data['employee_email'])
                
                allocation_to_update = Allocation.objects.get(asset=asset, employee=employee, transaction_status='Allocated')
                
                # Update all return fields
                for field_name, value in form.cleaned_data.items():
                    if hasattr(allocation_to_update, field_name):
                        setattr(allocation_to_update, field_name, value)
                
                allocation_to_update.returned_date = timezone.now()
                allocation_to_update.transaction_status = 'Returned'
                allocation_to_update.save()
                
                asset.status = 'Available'
                asset.save()
                return redirect('allocation_list')

    # For GET request or if a form was submitted with errors
    allocate_form = AllocationForm()
    return_form = ReturnForm()
    
    if request.method == 'POST':
        if request.POST.get('form_type') == 'allocate':
            allocate_form = AllocationForm(request.POST)
        elif request.POST.get('form_type') == 'return':
            # Re-populate the form with posted data and corrected queryset
            form_data = request.POST.copy()
            return_form = ReturnForm(form_data)
            if 'employee_email' in form_data:
                try:
                    employee = Employee.objects.get(email=form_data['employee_email'])
                    asset_ids = Allocation.objects.filter(employee=employee, transaction_status='Allocated').values_list('asset_id', flat=True)
                    return_form.fields['asset'].queryset = Asset.objects.filter(asset_id__in=asset_ids)
                except Employee.DoesNotExist:
                    return_form.add_error('employee_email', 'Employee not found.')
            
    context = {'allocation_form': allocate_form, 'return_form': return_form}
    return render(request, 'inventory/allocation_form.html', context)


# --- NAYI AJAX VIEWS ---
def get_asset_details(request):
    asset_id = request.GET.get('asset_id')
    try:
        asset = Asset.objects.get(asset_id=asset_id)
        data = {
            'brand': asset.brand,
            'processor': asset.processor,
        }
        return JsonResponse(data)
    except Asset.DoesNotExist:
        return JsonResponse({'error': 'Asset not found'}, status=404)

def get_employee_assets(request):
    email = request.GET.get('email')
    try:
        employee = Employee.objects.get(email=email)
        allocations = Allocation.objects.filter(employee=employee, transaction_status='Allocated')
        assets = [{'id': alloc.asset.asset_id, 'text': alloc.asset.serial_number} for alloc in allocations]
        return JsonResponse({'assets': assets})
    except Employee.DoesNotExist:
        return JsonResponse({'assets': []})


def add_asset(request):
    if request.method == 'POST':
        # Initialize forms to pass to context in case of errors
        asset_form = AssetForm()
        bulk_form = BulkAssetImportForm()
        
        if 'add_single_asset' in request.POST:
            asset_form = AssetForm(request.POST)
            if asset_form.is_valid():
                asset_form.save()
                messages.success(request, 'Asset has been successfully added!')
                return redirect('asset_list') # Redirect to asset list for better UX

        elif 'import_bulk_asset' in request.POST:
            bulk_form = BulkAssetImportForm(request.POST, request.FILES)
            if bulk_form.is_valid():
                csv_file = request.FILES['file']
                file = TextIOWrapper(csv_file.file, encoding='utf-8')
                reader = csv.DictReader(file)
                
                created_count = 0
                errors = []

                for row_num, row in enumerate(reader, 2):
                    try:
                        if not row.get('asset_id') or not row.get('serial_number'):
                            errors.append(f"Row {row_num}: asset_id and serial_number are required.")
                            continue
                        
                        Asset.objects.create(
                            asset_id=row.get('asset_id'),
                            serial_number=row.get('serial_number'),
                            asset_type=row.get('asset_type', 'Laptop'),
                            brand=row.get('brand'),
                            model=row.get('model'),
                            processor=row.get('processor'),
                            ram_gb=row.get('ram_gb') or None,
                            storage_size_gb=row.get('storage_size_gb') or None,
                            purchase_date=row.get('purchase_date') or None,
                            warranty_expiry=row.get('warranty_expiry') or None,
                            status=row.get('status', 'Available'),
                            remarks=row.get('remarks')
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error - {e}")
                
                if created_count > 0:
                    messages.success(request, f'Successfully imported {created_count} assets.')
                if errors:
                    for error in errors:
                        messages.error(request, error)

                return redirect('asset_list') # Redirect to asset list
    else:
        asset_form = AssetForm()
        bulk_form = BulkAssetImportForm()

    context = {
        'asset_form': asset_form,
        'bulk_form': bulk_form,
    }
    return render(request, 'inventory/add_asset.html', context)