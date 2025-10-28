# inventory/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Asset, Employee, Allocation, AuditLog
from .middleware import get_current_user

# A helper function to avoid repetitive code
def create_audit_log(actor, action_type, details):
    """Creates an AuditLog entry."""
    AuditLog.objects.create(
        actor=actor,
        action_type=action_type,
        details=details
    )

@receiver(post_save, sender=Allocation)
def log_allocation_change(sender, instance, created, **kwargs):
    """
    Logs the creation of an Allocation (Asset Assignment or Return).
    This signal fires whenever an Allocation record is saved.
    """
    user = get_current_user()
    
    # We only log actions performed by an authenticated user.
    # This prevents logging for actions from scripts or the shell.
    if not user:
        return

    # We only care about the initial creation of the allocation record.
    if created:
        # Construct a detailed description for the log.
        details = {
            "actor_name": user.get_full_name() or user.username,
            "asset_serial": instance.asset.serial_number,
            "asset_model": instance.asset.model,
            "employee_name": instance.employee.full_name,
            "allocation_id": instance.allocation_id
        }
        
        # Determine if it's an assignment or a return based on the form logic.
        # This assumes a 'returned_date' means it's a return transaction.
        action = "ASSET_RETURNED" if instance.returned_date else "ASSET_ASSIGNED"
        
        create_audit_log(user, action, details)

@receiver(post_save, sender=Asset)
def log_asset_save(sender, instance, created, **kwargs):
    """
    Logs the creation or update of an Asset.
    This action is restricted to Super Admins only.
    """
    user = get_current_user()
    if not user or not user.is_superuser:
        # Validation: If the user is not a superuser, do not log.
        # This enforces the rule that only Super Admins can manage the asset inventory.
        return
        
    details = {
        "actor_name": user.get_full_name() or user.username,
        "asset_id": instance.asset_id,
        "asset_serial": instance.serial_number,
        "asset_model": instance.model
    }
    
    if created:
        action = "ASSET_CREATED"
    else:
        action = "ASSET_UPDATED"
        
    create_audit_log(user, action, details)

@receiver(post_delete, sender=Asset)
def log_asset_delete(sender, instance, **kwargs):
    """
    Logs the deletion of an Asset.
    This action is restricted to Super Admins only.
    """
    user = get_current_user()
    if not user or not user.is_superuser:
        # Validation: Enforce that only Super Admins can delete assets.
        return

    details = {
        "actor_name": user.get_full_name() or user.username,
        "deleted_asset_id": instance.asset_id,
        "deleted_asset_serial": instance.serial_number,
        "deleted_asset_model": instance.model
    }
    
    create_audit_log(user, "ASSET_DELETED", details)

@receiver(post_save, sender=Employee)
def log_employee_save(sender, instance, created, **kwargs):
    """

    Logs the creation or update of an Employee record.
    Restricted to Super Admins.
    """
    user = get_current_user()
    if not user or not user.is_superuser:
        # Validation: Only Super Admins can manage employee records directly.
        return

    details = {
        "actor_name": user.get_full_name() or user.username,
        "employee_id": instance.employee_id,
        "employee_name": instance.full_name,
        "employee_email": instance.email
    }

    if created:
        action = "EMPLOYEE_CREATED"
    else:
        action = "EMPLOYEE_UPDATED"
        
    create_audit_log(user, action, details)

@receiver(post_delete, sender=Employee)
def log_employee_delete(sender, instance, **kwargs):
    """
    Logs the deletion of an Employee record.
    Restricted to Super Admins.
    """
    user = get_current_user()
    if not user or not user.is_superuser:
        # Validation: Only Super Admins can delete employee records.
        return

    details = {
        "actor_name": user.get_full_name() or user.username,
        "deleted_employee_id": instance.employee_id,
        "deleted_employee_name": instance.full_name,
        "deleted_employee_email": instance.email
    }
    
    create_audit_log(user, "EMPLOYEE_DELETED", details)