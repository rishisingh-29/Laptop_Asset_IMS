# inventory/decorators.py

from functools import wraps
from django.shortcuts import redirect

def role_required(allowed_roles=()):
    """
    A decorator to restrict view access based on user group membership.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            
            # Validation 1: User must be logged in.
            if not request.user.is_authenticated:
                # Redirect to the namespaced login URL.
                return redirect('inventory:login')

            # Validation 2: Superusers are always allowed access.
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Validation 3: Check if the user is in any of the allowed groups.
            if request.user.groups.filter(name__in=allowed_roles).exists():
                return view_func(request, *args, **kwargs)
            else:
                # ===================================================================
                # THE FIX: Added the 'inventory:' namespace to the redirect URL.
                # ===================================================================
                # If all checks fail, the user is not authorized. Redirect them
                # to the correctly namespaced 'access_denied' page.
                return redirect('inventory:access_denied')
                
        return wrapper_func
    return decorator