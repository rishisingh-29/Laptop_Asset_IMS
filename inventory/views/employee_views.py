# inventory/views/employee_views.py

import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from ..models import Employee, Allocation
from ..forms import EmployeeForm, BulkEmployeeImportForm
from ..decorators import role_required

@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def employee_list(request):
    """
    Displays a paginated and searchable list of all employees.
    """
    active_allocations_prefetch = Prefetch(
        'allocations',
        queryset=Allocation.objects.filter(transaction_status='Allocated').select_related('asset'),
        to_attr='active_allocations'
    )
    
    employee_queryset = Employee.objects.prefetch_related(active_allocations_prefetch).order_by('full_name')

    query = request.GET.get('q')
    if query:
        employee_queryset = employee_queryset.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(designation__icontains=query)
        )

    paginator = Paginator(employee_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'inventory/employees/employee_list.html', context)


@login_required
@role_required(allowed_roles=['Super_Admin'])
def add_employee(request, pk=None):
    """
    Handles both adding a new employee and editing an existing one.
    """
    instance = get_object_or_404(Employee, pk=pk) if pk else None
    
    if request.method == 'POST':
        if 'add_single_employee' in request.POST:
            employee_form = EmployeeForm(request.POST, instance=instance)
            if employee_form.is_valid():
                employee_form.save()
                messages.success(request, f"Employee '{employee_form.cleaned_data['full_name']}' has been successfully saved!")
                return redirect('inventory:employee_list')
            else:
                bulk_form = BulkEmployeeImportForm()
        
        elif 'import_bulk_employee' in request.POST:
            bulk_form = BulkEmployeeImportForm(request.POST, request.FILES)
            if bulk_form.is_valid():
                handle_bulk_employee_import(request, bulk_form)
                return redirect('inventory:employee_list')
            else:
                employee_form = EmployeeForm(instance=instance)
    
    else: # For a GET request
        employee_form = EmployeeForm(instance=instance)
        bulk_form = BulkEmployeeImportForm()

    context = {
        'employee_form': employee_form,
        'bulk_form': bulk_form,
        'employee': instance,
    }
    return render(request, 'inventory/employees/employee_form.html', context)


@login_required
@role_required(allowed_roles=['Super_Admin'])
def delete_employee(request, pk):
    """
    Handles the deletion of an employee after confirmation.
    """
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('inventory:employee_list')

    employee = get_object_or_404(Employee, pk=pk)
    
    # Validation: An employee cannot be deleted if they have allocated assets.
    if Allocation.objects.filter(employee=employee, transaction_status='Allocated').exists():
        messages.error(request, f"Cannot delete '{employee.full_name}' because they have active allocated assets. Please return all assets first.")
        return redirect('inventory:employee_list')
        
    try:
        employee_name = employee.full_name
        employee.delete()
        messages.success(request, f"Employee '{employee_name}' has been successfully deleted.")
    except Exception as e:
        messages.error(request, f"An error occurred while trying to delete the employee: {e}")

    return redirect('inventory:employee_list')


def handle_bulk_employee_import(request, form):
    """
    Helper function to process the uploaded CSV for bulk employee import.
    """
    # This function remains unchanged.
    csv_file = form.cleaned_data['file']
    file = TextIOWrapper(csv_file.file, encoding='utf-8')
    reader = csv.DictReader(file)

    created_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, 2):
        try:
            full_name = row.get('full_name')
            email = row.get('email')
            if not full_name or not email:
                errors.append(f"Row {row_num}: `full_name` and `email` are required.")
                continue

            employee, created = Employee.objects.update_or_create(
                email=email,
                defaults={
                    'full_name': full_name,
                    'designation': row.get('designation'),
                    'status': row.get('status', 'Active'),
                    'date_of_joining': row.get('date_of_joining') or None,
                }
            )
            if created:
                created_count += 1
        except IntegrityError:
            errors.append(f"Row {row_num}: Employee with email '{email}' might already exist.")
        except Exception as e:
            errors.append(f"Row {row_num}: An unexpected error occurred - {e}")

    if created_count > 0:
        messages.success(request, f'Successfully imported {created_count} new employees.')
    if not errors and created_count == 0:
        messages.info(request, 'No new employees were imported. The data may have matched existing records.')
    if errors:
        error_message = "Bulk import finished with some errors: " + " | ".join(errors)
        messages.error(request, error_message)