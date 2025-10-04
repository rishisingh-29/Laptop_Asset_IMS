from django import forms
from .models import Allocation, Asset, Employee 
from django.core.exceptions import ValidationError # Needed for validation

# Define common choices
ASSET_PROPERTY_CHOICES = [
    ('', '--- Select an Option ---'),
    ('Good', 'Good'),
    ('Damaged', 'Damaged'),
    ('Not Working', 'Not Working'),
    ('Missing', 'Missing'),
]

ALLOCATION_TYPE_CHOICES = [
    ('in_person', 'In Person'),
    ('courier', 'Courier'),
]


class AllocationForm(forms.ModelForm):
    # Form Field 1: Fields to link to Foreign Keys
    # We use EmailField/ModelChoiceField to look up the related objects in views.py
    employee_email = forms.EmailField(label='Employee Email')
    it_spoc_email = forms.EmailField(label='IT SPOC Email ID')
    
    asset_id = forms.ModelChoiceField(
        queryset=Asset.objects.filter(status='available').order_by('serial_no'), # Check the status value is correct
        to_field_name='serial_no', 
        label='Available Asset ID (Serial No.)',
        empty_label='--- Select Available Asset ---',
    )
    
    # Form Field 2: Custom fields for recording details (not saved to Allocation model)
    asset_make = forms.CharField(label='Asset Make', required=False)
    asset_processor = forms.CharField(label='Asset Processor', required=False)
    keyboard_touchpad = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Keyboard and Touchpad', required=False)
    charger = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Charger', required=False)
    bag = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Bag', required=False)
    condition = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Condition', required=False)
    allocation_location = forms.CharField(label='Allocation Location', required=False)
    
    # Form Field 3: Fields that align with Allocation model (type and reason)
    # We must rename 'allocation_type' to 'allocation_method' to avoid conflict with model field 'type'
    allocation_method = forms.ChoiceField( 
        choices=ALLOCATION_TYPE_CHOICES, 
        widget=forms.RadioSelect, 
        label='Allocation Type (In Person/Courier)'
    )
    requirement_reason = forms.CharField(label='Asset Requirement Reason', widget=forms.Textarea(attrs={'rows': 3}))
    assigned_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Allocation
        # We only use the model fields here that align with the form/save process
        # We will use the view to map custom form fields to model Foreign Keys (employee, asset)
        fields = ['type', 'reason', 'assigned_date'] 
        # Note: 'type' will be set to 'New' in the view.
        # Note: 'reason' will be mapped to 'requirement_reason' in the view.
        
    def clean(self):
        cleaned_data = super().clean()
        employee_email = cleaned_data.get('employee_email')
        
        # Check if the Employee exists before trying to allocate
        if employee_email:
            try:
                Employee.objects.get(email=employee_email)
            except Employee.DoesNotExist:
                raise forms.ValidationError(
                    "The Employee Email provided does not exist in the system. Please register the employee first."
                )
        return cleaned_data
        
# ----------------------------------------------------------------------------------

class ReturnForm(forms.ModelForm):
    # Form Field 1: Fields to link to Foreign Keys
    employee_email = forms.EmailField(label='Employee Email')
    it_spoc_email = forms.EmailField(label='IT SPOC Email ID')
    
    asset_id = forms.ModelChoiceField(
        # Filter for assets currently allocated/in-use
        queryset=Asset.objects.filter(status='allocated').order_by('serial_no'), 
        to_field_name='serial_no',
        label='Allocated Asset ID (Serial No.)',
        empty_label='--- Select Allocated Asset ---',
    )
    
    # Form Field 2: Custom fields for return details
    return_location = forms.CharField(label='Asset Return Location', required=False)
    purpose = forms.CharField(label='Purpose (Not Used in Model)', required=False) # No corresponding model field
    return_reason = forms.CharField(label='Asset Return Reason', required=False)
    remarks = forms.CharField(label='Remarks', widget=forms.Textarea(attrs={'rows': 3}), required=False)
    return_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Condition fields
    power_status = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Power Status', required=False)
    screen = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Screen Condition', required=False)
    return_charger = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Return Charger', required=False)
    return_bag = forms.ChoiceField(choices=ASSET_PROPERTY_CHOICES, label='Return Bag', required=False)
    
    # Radio button
    return_method = forms.ChoiceField(choices=ALLOCATION_TYPE_CHOICES, widget=forms.RadioSelect, label='Return Type (In Person/Courier)')
    
    class Meta:
        model = Allocation 
        fields = ['status', 'returned_date', 'type', 'reason'] # Fields to update on the Allocation object
        # Note: 'status' will be set to 'Returned' in the view.
        # Note: 'type' will be set to 'Return' in the view.

    def clean(self):
        # We need to ensure the asset being returned is actually in an 'Allocated' state
        cleaned_data = super().clean()
        asset = cleaned_data.get('asset_id')
        if asset and asset.status != 'allocated':
             raise forms.ValidationError(
                f"Asset {asset.serial_no} is currently marked as {asset.status}. It cannot be returned."
            )
        
        # Check if the employee email matches the asset's current allocation
        employee_email = cleaned_data.get('employee_email')
        if asset and employee_email:
            try:
                current_allocation = Allocation.objects.get(asset=asset, status='Allocated')
                if current_allocation.employee.email != employee_email:
                     raise forms.ValidationError(
                        "The asset is currently allocated to a different employee."
                    )
            except Allocation.DoesNotExist:
                # This should not happen if the asset status is 'allocated', but check anyway
                raise forms.ValidationError(
                    "Asset is not currently listed as allocated in the Allocation table."
                )
        return cleaned_data