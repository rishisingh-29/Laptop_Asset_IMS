from django.db import models

# Create your models here.
class Employee(models.Model):
    employee_id = models.IntegerField(unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('inactive', 'Inactive')],
        default='active'
    )
    employee_type = models.CharField(
        max_length=10,
        choices=[('Permanent', 'Permanent'), ('Contract', 'Contract'), ('Intern', 'Intern')]
    )
    date_of_joining = models.DateField()
    designation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

#Asset Model
class Asset(models.Model):
    serial_no = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('allocated', 'Allocated'),
            ('retired', 'Retired'),
            ('under repair', 'Under Repair')
        ],
        default='available'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.serial_no


#allocation Model
class Allocation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=10,
        choices=[
            ('New', 'New'),
            ('Return', 'Return'),
            ('Replace', 'Replace'),
            ('Repair', 'Repair'),
            ('Additional', 'Additional')
        ]
    )
    status = models.CharField(
        max_length=15,
        choices=[
            ('Allocated', 'Allocated'),
            ('Returned', 'Returned'),
            ('In Repair', 'In Repair')
        ]
    )
    reason = models.TextField()
    assigned_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.full_name} - {self.asset.serial_no}"
    
#history
class AllocationHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=10, choices=[
        ('New', 'New'),
        ('Return', 'Return'),
        ('Replace', 'Replace'),
        ('Repair', 'Repair'),
        ('Additional', 'Additional')
    ])
    status = models.CharField(max_length=15, choices=[
        ('Allocated', 'Allocated'),
        ('Returned', 'Returned'),
        ('In Repair', 'In Repair')
    ])
    reason = models.TextField()
    assigned_date = models.DateField(null=True, blank=True)
    returned_date = models.DateField(null=True, blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History: {self.employee} - {self.asset}"
