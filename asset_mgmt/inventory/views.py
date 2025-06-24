from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Asset, Allocation
from .forms import AllocationForm
from django.db.models import Q

def home(request):
    total_employees = Employee.objects.filter(status='active').count()
    total_assets = Asset.objects.count()
    assigned_assets = Asset.objects.filter(status='allocated').count()
    unassigned_assets = Asset.objects.filter(status='available').count()
    health_check_assets = Asset.objects.filter(status='under repair').count()
    
    employees = Employee.objects.all()

    context = {
        'total_employees': total_employees,
        'total_assets': total_assets,
        'assigned_assets': assigned_assets,
        'unassigned_assets': unassigned_assets,
        'health_check_assets': health_check_assets,
        'employees': employees,
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
    return render(request, 'inventory/asset_list.html', {'assets': assets})

def allocation_list(request):
    allocations = Allocation.objects.select_related('employee', 'asset')
    return render(request, 'inventory/allocation_list.html', {'allocations': allocations})

def allocate_asset(request):
    if request.method == 'POST':
        form = AllocationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('allocation_list')
    else:
        form = AllocationForm()
    return render(request, 'inventory/allocation_form.html', {'form': form})
