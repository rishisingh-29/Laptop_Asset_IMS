# inventory/models.py
from django.db import models

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='Active')
    designation = models.CharField(max_length=255, null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    class Meta: db_table = 'inventory_employee'
    def __str__(self): return self.full_name

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
    class Meta: db_table = 'inventory_asset'
    def __str__(self): return self.serial_number

class Allocation(models.Model):
    allocation_id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, db_column='asset_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, db_column='employee_id')
    it_spoc_employee_id = models.IntegerField(null=True, blank=True)
    
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
    class Meta: db_table = 'inventory_allocation'
    def __str__(self): return f"{self.employee.full_name} - {self.asset.serial_number}"