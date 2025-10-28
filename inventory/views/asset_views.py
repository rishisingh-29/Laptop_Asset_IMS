# inventory/views/asset_views.py

import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from ..models import Asset
from ..forms import AssetForm, BulkAssetImportForm
from ..decorators import role_required

@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def asset_list(request):
    """
    Displays a paginated and searchable list of all assets.
    """
    asset_queryset = Asset.objects.all().order_by('asset_id')
    
    query = request.GET.get('q')
    if query:
        asset_queryset = asset_queryset.filter(
            Q(asset_id__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(model__icontains=query) |
            Q(brand__icontains=query)
        )

    paginator = Paginator(asset_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    status_counts_json = list(Asset.objects.values('status').annotate(count=Count('status')))

    context = {
        'page_obj': page_obj,
        'status_counts_json': status_counts_json,
        'query': query,
    }
    return render(request, 'inventory/assets/asset_list.html', context)


@login_required
@role_required(allowed_roles=['Super_Admin'])
def add_asset(request, pk=None):
    """
    Handles both adding a new asset and editing an existing asset.
    Also handles bulk import.
    """
    # Check if we are editing an existing asset
    instance = get_object_or_404(Asset, pk=pk) if pk else None
    
    if request.method == 'POST':
        if 'add_single_asset' in request.POST:
            # Pass the instance to the form if we are editing
            asset_form = AssetForm(request.POST, instance=instance)
            if asset_form.is_valid():
                asset_form.save()
                messages.success(request, f"Asset '{asset_form.cleaned_data['serial_number']}' has been successfully saved!")
                return redirect('inventory:asset_list')
            else:
                bulk_form = BulkAssetImportForm()
        
        elif 'import_bulk_asset' in request.POST:
            bulk_form = BulkAssetImportForm(request.POST, request.FILES)
            if bulk_form.is_valid():
                handle_bulk_asset_import(request, bulk_form)
                return redirect('inventory:asset_list')
            else:
                asset_form = AssetForm(instance=instance)
    
    else: # For a GET request
        asset_form = AssetForm(instance=instance)
        bulk_form = BulkAssetImportForm()

    context = {
        'asset_form': asset_form,
        'bulk_form': bulk_form,
        'asset': instance,  # Pass asset to template to change titles (Add/Edit)
    }
    return render(request, 'inventory/assets/asset_form.html', context)


@login_required
@role_required(allowed_roles=['Super_Admin'])
def delete_asset(request, pk):
    """
    Handles the deletion of an asset after confirmation.
    """
    # Validation: Only POST requests are allowed for deletion
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('inventory:asset_list')

    asset = get_object_or_404(Asset, pk=pk)
    
    # Validation: An asset cannot be deleted if it is currently allocated
    if asset.status == 'Allocated':
        messages.error(request, f"Cannot delete asset '{asset.serial_number}' because it is currently allocated. Please process its return first.")
        return redirect('inventory:asset_list')
        
    try:
        asset_serial = asset.serial_number
        asset.delete()
        messages.success(request, f"Asset '{asset_serial}' has been successfully deleted.")
    except Exception as e:
        messages.error(request, f"An error occurred while trying to delete the asset: {e}")

    return redirect('inventory:asset_list')


def handle_bulk_asset_import(request, form):
    """
    Helper function to process the uploaded CSV file for bulk asset import.
    """
    # This function remains unchanged.
    csv_file = form.cleaned_data['file']
    file = TextIOWrapper(csv_file.file, encoding='utf-8')
    reader = csv.DictReader(file)
    
    created_count = 0
    errors = []
    
    for row_num, row in enumerate(reader, 2):
        try:
            asset_id = row.get('asset_id')
            serial_number = row.get('serial_number')
            if not asset_id or not serial_number:
                errors.append(f"Row {row_num}: `asset_id` and `serial_number` are required fields.")
                continue

            asset, created = Asset.objects.update_or_create(
                asset_id=asset_id,
                defaults={
                    'serial_number': serial_number,
                    'asset_type': row.get('asset_type', 'Laptop'),
                    'brand': row.get('brand'),
                    'model': row.get('model'),
                    'processor': row.get('processor'),
                    'ram_gb': int(row.get('ram_gb')) if row.get('ram_gb') else None,
                    'storage_size_gb': int(row.get('storage_size_gb')) if row.get('storage_size_gb') else None,
                    'purchase_date': row.get('purchase_date') or None,
                    'warranty_expiry': row.get('warranty_expiry') or None,
                    'status': row.get('status', 'Available'),
                    'remarks': row.get('remarks')
                }
            )
            if created:
                created_count += 1
        except IntegrityError:
            errors.append(f"Row {row_num}: A database error occurred. The serial number '{serial_number}' might already exist.")
        except Exception as e:
            errors.append(f"Row {row_num}: An unexpected error occurred - {e}")
    
    if created_count > 0:
        messages.success(request, f'Successfully imported {created_count} new assets.')
    if not errors and created_count == 0:
        messages.info(request, 'No new assets were imported. The data may have matched existing records.')
    if errors:
        error_message = "Bulk import finished with some errors: " + " | ".join(errors)
        messages.error(request, error_message)