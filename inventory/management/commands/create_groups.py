# inventory/management/commands/create_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
import logging

# It's a good practice to use a logger for management commands
# for more structured output, but for this simple case, self.stdout is perfectly fine.

class Command(BaseCommand):
    """
    A Django management command to initialize the application's user roles (Groups).

    This command is idempotent, meaning it can be run multiple times without
    creating duplicate groups or causing errors. It's an essential part of the
    deployment and setup process for the application.

    To run this command:
    $ python manage.py create_groups
    """
    
    help = 'Creates the initial user groups required for the application: Employee, IT_Admin, and Super_Admin.'

    def handle(self, *args, **kwargs):
        """
        The main logic of the command.
        """
        self.stdout.write(self.style.MIGRATE_HEADING('Starting to create required user groups...'))

        # Define the core user roles for the entire application.
        # These names are used by the @role_required decorator and in views
        # to control access to different features.
        GROUPS_TO_CREATE = ['Employee', 'IT_Admin', 'Super_Admin']
        
        groups_created_count = 0
        groups_existing_count = 0

        for group_name in GROUPS_TO_CREATE:
            # The get_or_create method is the key to making this command safe to run multiple times.
            # It checks if a group with the given name already exists.
            # - If it exists, it retrieves it. `created` will be False.
            # - If it does not exist, it creates it. `created` will be True.
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Provide clear feedback in the console for each group.
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Group '{group_name}' was created successfully."))
                groups_created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"✓ Group '{group_name}' already exists. Skipping."))
                groups_existing_count += 1
        
        self.stdout.write(self.style.MIGRATE_HEADING("\nGroup creation process finished."))
        self.stdout.write(f"Summary: {groups_created_count} groups created, {groups_existing_count} groups already existed.")