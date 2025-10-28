# inventory/views/log_views.py

from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from ..models import AuditLog
from ..decorators import role_required

@login_required
@role_required(allowed_roles=['IT_Admin', 'Super_Admin'])
def audit_log_viewer(request):
    """
    Displays a searchable and filterable view of the AuditLog.
    Access is restricted to IT Admins and Super Admins, with different
    data visibility for each role.
    """
    # Base queryset for logs
    log_queryset = AuditLog.objects.select_related('actor').order_by('-timestamp')

    # ===================================================================
    # ROLE-BASED VISIBILITY VALIDATION
    # ===================================================================
    # If the user is an IT Admin but not a Super Admin, restrict their view.
    if not request.user.is_superuser and request.user.groups.filter(name='IT_Admin').exists():
        # IT Admins can only see logs from other IT Admins.
        it_admin_group = Group.objects.get(name='IT_Admin')
        log_queryset = log_queryset.filter(actor__groups=it_admin_group)
        # They also cannot see sensitive deletion logs.
        log_queryset = log_queryset.exclude(action_type__icontains='DELETED')

    # Super Admins can see everything, so no additional filtering is needed for them.

    # --- Filtering and Searching ---
    query = request.GET.get('query', '').strip()
    actor_id = request.GET.get('actor')
    action_type = request.GET.get('action_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if query:
        # A flexible search across the JSON 'details' field
        log_queryset = log_queryset.filter(
            Q(details__icontains=query) |
            Q(actor__username__icontains=query) |
            Q(actor__first_name__icontains=query) |
            Q(actor__last_name__icontains=query)
        )
    
    if actor_id:
        log_queryset = log_queryset.filter(actor_id=actor_id)

    if action_type:
        log_queryset = log_queryset.filter(action_type=action_type)
    
    if start_date:
        log_queryset = log_queryset.filter(timestamp__date__gte=start_date)

    if end_date:
        log_queryset = log_queryset.filter(timestamp__date__lte=end_date)
        
    # Pagination
    paginator = Paginator(log_queryset, 20) # Show 20 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get a list of possible admins to populate the filter dropdown
    admin_users = User.objects.filter(
        Q(is_superuser=True) | Q(groups__name__in=['IT_Admin', 'Super_Admin'])
    ).distinct().order_by('username')
    
    # Get a list of unique action types present in the log for the filter dropdown
    action_types = AuditLog.objects.values_list('action_type', 'action_type').distinct()

    context = {
        'page_obj': page_obj,
        'admin_users': admin_users,
        'action_types': action_types,
    }
    return render(request, 'inventory/logs/audit_log_viewer.html', context)