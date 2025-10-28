# inventory/forms.py

from django import forms
from django.contrib.auth.models import User, Group
from .models import Allocation, Asset, Employee, AuditLog

# ===================================================================
# NEW: User Registration and Authentication Forms
# ===================================================================
ROLE_CHOICES = [
    ('Employee', 'Employee'),
    ('IT_Admin', 'IT Admin'),
]

class UserRegistrationForm(forms.ModelForm):
    """Form for handling new user registration."""
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    full_name = forms.CharField(max_length=255, label="Full Name")
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'role')

    def clean_password2(self):
        """Validation: Ensure that the two password fields match."""
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cd.get('password2')

    def clean_email(self):
        """Validation: Ensure the email address is unique across all Users."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

# ===================================================================
# NEW: Audit Log Filter Form
# ===================================================================
class AuditLogFilterForm(forms.Form):
    """A non-model form used to filter the audit log viewer page."""
    query = forms.CharField(required=False, label="Search Details")
    # Note: The querysets for the choices will be set dynamically in the view.
    actor = forms.ChoiceField(choices=[('', 'All Users')], required=False, label="Performed By")
    action_type = forms.ChoiceField(choices=[('', 'All Actions')], required=False, label="Action Type")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

# ===================================================================
# PRESERVED: Your Existing Allocation Forms
# ===================================================================
CHOICES_ASSET_CONDITION = [('', 'Select Condition'), ('No Damage', 'No Damage'), ('Damage', 'Damage'), ('Flickering', 'Flickering')]
CHOICES_KEYBOARD_TOUCHPAD = [('', 'Select Keyboard and Touchpad'), ('Working', 'Working'), ('Not Working', 'Not Working'), ('Damage', 'Damage')]
CHOICES_CHARGER_BAG = [('', 'Select Status'), ('Allocated', 'Allocated'), ('Not Allocated', 'Not Allocated')]
CHOICES_REQUIREMENT_REASON = [('', 'Select Asset Requirement Reason'), ('New Joiner', 'New Joiner'), ('Replacement', 'Replacement'), ('Additional', 'Additional')]
CHOICES_POWER_STATUS = [('', 'Select Asset Power Status'), ('Power On', 'Power On'), ('No Power', 'No Power')]
CHOICES_SCREEN_STATUS = [('', 'Select Screen'), ('No Damage', 'No Damage'), ('Damage', 'Damage'), ('Flickering', 'Flickering')]
CHOICES_PURPOSE = [('', 'Select Purpose'), ('Resignation', 'Resignation'), ('Upgrade', 'Upgrade'), ('Termination', 'Termination')]
CHOICES_RETURN_REASON = [('', 'Select Asset Return Reason'), ('Exit Employee', 'Exit Employee'), ('Replacement', 'Replacement')]
CHOICES_RETURN_STATUS = [('', 'Select Status'), ('Returned', 'Returned'), ('Not Returned', 'Not Returned'), ('Damaged', 'Damaged')]

class AllocationForm(forms.ModelForm):
    employee_email = forms.EmailField(label='Employee Email')
    asset_make = forms.CharField(label='Asset Make', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    asset_processor = forms.CharField(label='Asset Processor', required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = Allocation
        fields = [
            'employee_email', 'asset', 'it_spoc_employee_id', 'allocation_reason',
            'asset_make', 'asset_processor', 'keyboard_and_touchpad_status',
            'charger_status', 'allocation_location', 'bag_status', 'delivery_type',
            'asset_condition_on_alloc', 'assigned_date', 'allocation_docket_id'
        ]
        widgets = {
            'asset': forms.Select, 'allocation_reason': forms.Select(choices=CHOICES_REQUIREMENT_REASON),
            'keyboard_and_touchpad_status': forms.Select(choices=CHOICES_KEYBOARD_TOUCHPAD),
            'charger_status': forms.Select(choices=CHOICES_CHARGER_BAG), 'bag_status': forms.Select(choices=CHOICES_CHARGER_BAG),
            'asset_condition_on_alloc': forms.Select(choices=CHOICES_ASSET_CONDITION),
            'delivery_type': forms.RadioSelect(choices=[('In Person', 'In Person'), ('Courier', 'Courier')]),
            'assigned_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only available assets in the dropdown
        self.fields['asset'].queryset = Asset.objects.filter(status__iexact='Available').order_by('asset_id')


class ReturnForm(forms.ModelForm):
    employee_email = forms.EmailField(label='Employee Email')
    class Meta:
        model = Allocation
        fields = [
            'employee_email', 'asset', 'it_spoc_employee_id', 'return_location',
            'asset_power_status', 'asset_screen_status', 'purpose', 'remarks',
            'return_reason', 'delivery_type', 'charger_return_status',
            'bag_return_status', 'returned_date', 'return_docket_id'
        ]
        widgets = {
            'asset': forms.Select, 'asset_power_status': forms.Select(choices=CHOICES_POWER_STATUS),
            'asset_screen_status': forms.Select(choices=CHOICES_SCREEN_STATUS), 'purpose': forms.Select(choices=CHOICES_PURPOSE),
            'return_reason': forms.Select(choices=CHOICES_RETURN_REASON),
            'charger_return_status': forms.Select(choices=CHOICES_RETURN_STATUS), 'bag_return_status': forms.Select(choices=CHOICES_RETURN_STATUS),
            'delivery_type': forms.RadioSelect(choices=[('In Person', 'In Person'), ('Courier', 'Courier')]),
            'returned_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

# ===================================================================
# PRESERVED: Your Existing Asset Forms
# ===================================================================
class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'asset_id', 'serial_number', 'asset_type', 
            'brand', 'model', 'processor', 'ram_gb', 
            'storage_size_gb', 'purchase_date', 'warranty_expiry', 
            'status', 'remarks'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('', 'Select Status'),
            ('Available', 'Available'),
            ('Allocated', 'Allocated'),
            ('Under Repair', 'Under Repair'),
            ('Retired', 'Retired'),
        ]
        self.fields['asset_type'].initial = 'Laptop'

class BulkAssetImportForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")

# ===================================================================
# PRESERVED: Your Existing Employee Forms
# ===================================================================
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'designation', 'status', 'date_of_joining']
        widgets = {
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
            ('On Leave', 'On Leave'),
        ]

class BulkEmployeeImportForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")