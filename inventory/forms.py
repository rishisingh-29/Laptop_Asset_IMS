# inventory/forms.py
from django import forms
from .models import Allocation, Asset, Employee

# --- CHOICES ---
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