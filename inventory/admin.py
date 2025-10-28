# inventory/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Employee, Asset, Allocation, AuditLog

# ===================================================================
# User and Employee Admin Configuration
# ===================================================================
# This connects the Employee profile directly into the User admin page
# for easier management.

class EmployeeInline(admin.StackedInline):
    """Makes the Employee model editable directly within the User admin page."""
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    """Extends the default User admin to include the inline Employee profile."""
    inlines = (EmployeeInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

# Unregister the default User admin and register our custom one.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ===================================================================
# Asset and Allocation Admin Configuration
# ===================================================================
# These are standard registrations for day-to-day data management.

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'brand', 'model', 'serial_number', 'status', 'purchase_date')
    list_filter = ('status', 'brand', 'asset_type')
    search_fields = ('asset_id', 'serial_number', 'model', 'brand')

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'asset', 'assigned_date', 'returned_date', 'transaction_status')
    list_filter = ('transaction_status',)
    search_fields = ('employee__full_name', 'asset__serial_number')


# ===================================================================
# Audit Log Admin Configuration (CRITICAL: READ-ONLY)
# ===================================================================
# This configuration ensures that the audit log is immutable from the admin panel.

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Configures the admin interface for the AuditLog model to be strictly read-only.
    This is a critical security feature to ensure the integrity of the audit trail.
    """
    # Fields to display in the list view
    list_display = ('timestamp', 'actor', 'action_type', 'formatted_details')
    # Filters for easier navigation
    list_filter = ('action_type', 'actor')
    # Search functionality
    search_fields = ('actor__username', 'details__asset_serial', 'details__employee_name')
    # Order by most recent first
    ordering = ('-timestamp',)

    def formatted_details(self, obj):
        """A custom method to display the JSON details in a more readable format."""
        # This is a simple representation; you can format it further if needed.
        return str(obj.details)
    formatted_details.short_description = 'Details'

    # --- PERMISSION VALIDATIONS ---
    # The following methods prevent any modification or creation of logs.

    def has_add_permission(self, request):
        """Prevents anyone from adding new log entries via the admin interface."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevents anyone from editing existing log entries."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevents anyone from deleting log entries."""
        return False