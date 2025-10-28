# inventory/templatetags/auth_extras.py

from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    A custom template filter to check if a user belongs to a specific group.
    
    This is the "Django way" to handle role-checking logic within templates,
    keeping the templates clean and the logic in Python.

    Usage in a template:
    {% load auth_extras %}
    ...
    {% if request.user|has_group:"IT_Admin" %}
        <!-- Content for IT Admins -->
    {% endif %}
    """
    # Validation: Ensure the user object is valid and authenticated
    if not hasattr(user, 'groups'):
        return False
        
    try:
        # Check if a group with the given name exists in the user's groups
        return user.groups.filter(name=group_name).exists()
    except Group.DoesNotExist:
        # Fails safely if the group somehow doesn't exist
        return False

@register.filter(name='is_in_groups')
def is_in_groups(user, group_names):
    """
    Checks if a user belongs to any of the groups in a comma-separated string.
    
    Usage in a template:
    {% if request.user|is_in_groups:"IT_Admin,Super_Admin" %}
    """
    if not hasattr(user, 'groups'):
        return False
    
    # Split the string of group names into a list
    group_list = [name.strip() for name in group_names.split(',')]
    return user.groups.filter(name__in=group_list).exists()