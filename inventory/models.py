# inventory/models.py

from django.db import models
from django.contrib.auth.models import User

# ===================================================================
# Employee Model
# ===================================================================
class Employee(models.Model):
    # OneToOneField creates a direct link to a Django User.
    # This is essential for tying employee profiles to login accounts.
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='employee_profile')
    
    employee_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, help_text="Must be a unique email address.")
    status = models.CharField(max_length=50, default='Active')
    designation = models.CharField(max_length=255, null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'inventory_employee'
        ordering = ['full_name'] # Good practice to have a default order

    def __str__(self):
        return self.full_name

# ===================================================================
# Asset Model
# ===================================================================
class Asset(models.Model):
    asset_id = models.CharField(max_length=50, primary_key=True)
    asset_type = models.CharField(max_length=50, default='Laptop')
    brand = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    serial_number = models.CharField(max_length=255, unique=True)
    processor = models.CharField(max_length=255, null=True, blank=True)
    ram_gb = models.IntegerField(null=True, blank=True)
    storage_size_gb = models.IntegerField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Available')
    remarks = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'inventory_asset'
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.brand} {self.model} ({self.serial_number})"

# ===================================================================
# Allocation (Transaction) Model
# ===================================================================
class Allocation(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    # Using related_name allows for easier reverse lookups, e.g., employee.allocations.all()
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, db_column='asset_id', related_name='allocations')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='employee_id', related_name='allocations')
    it_spoc_employee_id = models.IntegerField(null=True, blank=True, help_text="ID of the IT admin handling the transaction.")
    
    # Allocation Details
    assigned_date = models.DateTimeField(null=True, blank=True)
    allocation_reason = models.CharField(max_length=255, null=True, blank=True)
    asset_condition_on_alloc = models.CharField(max_length=255, null=True, blank=True)
    charger_status = models.CharField(max_length=50, null=True, blank=True)
    bag_status = models.CharField(max_length=50, null=True, blank=True)
    keyboard_and_touchpad_status = models.CharField(max_length=50, null=True, blank=True)
    allocation_location = models.CharField(max_length=255, null=True, blank=True)
    delivery_type = models.CharField(max_length=50, null=True, blank=True)
    allocation_docket_id = models.CharField(max_length=100, null=True, blank=True)

    # Return Details
    returned_date = models.DateTimeField(null=True, blank=True)
    return_reason = models.CharField(max_length=255, null=True, blank=True)
    purpose = models.CharField(max_length=255, null=True, blank=True)
    asset_power_status = models.CharField(max_length=50, null=True, blank=True)
    asset_screen_status = models.CharField(max_length=50, null=True, blank=True)
    charger_return_status = models.CharField(max_length=50, null=True, blank=True)
    bag_return_status = models.CharField(max_length=50, null=True, blank=True)
    return_location = models.CharField(max_length=255, null=True, blank=True)
    return_docket_id = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    
    transaction_status = models.CharField(max_length=50, default='Allocated')
    
    class Meta:
        db_table = 'inventory_allocation'
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.asset.serial_number}"

# ===================================================================
# Audit Log Model
# This model is the cornerstone of the logging and accountability system.
# ===================================================================
class AuditLog(models.Model):
    # Using a ForeignKey to User allows us to know who performed the action.
    # on_delete=models.SET_NULL ensures that if a user is deleted, their logs remain
    # but are attributed to a "deleted user".
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='actions')
    
    # A short, machine-readable code for the type of action performed.
    action_type = models.CharField(max_length=50)
    
    # Automatically records the timestamp when the log is created.
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # JSONField is a flexible way to store rich, structured data about the event.
    # This is where we'll save details like serial numbers, employee names, etc.
    details = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp'] # Always show the most recent logs first.

    # ===================================================================
    # THE FIX: Added a property to format the action_type for display.
    # ===================================================================
    @property
    def formatted_action_type(self):
        """Replaces underscores with spaces and applies title case for clean display."""
        return self.action_type.replace('_', ' ').title()

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"{actor_name} performed {self.action_type} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"