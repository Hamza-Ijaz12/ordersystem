from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError

def validate_numeric_phone(value):
    # Remove non-numeric characters
    numeric_value = ''.join(char for char in value if char.isdigit())

    if len(numeric_value) != 10:
        raise ValidationError('Phone number must have exactly 10 digits.')

class AddressForm(forms.Form):
    name = forms.CharField(label='Name')
    street1 = forms.CharField(label='Street 1')
    street2 = forms.CharField(label='apt/suite', required=False)
    city = forms.CharField(label='City')
    state = forms.CharField(label='State')
    zip = forms.CharField(label='ZIP Code')
    country = forms.CharField(label='Country')
    phone = forms.CharField(label='Phone', required=False,
                            validators=[validate_numeric_phone])

class ParcelForm(forms.Form):
    weight_lb = forms.FloatField(label='weight_lb', min_value=0)
    weight_oz = forms.FloatField(label='weight_oz', min_value=0)
    length = forms.FloatField(label='Length', required=False, )
    width = forms.FloatField(label='Width', required=False, )
    height = forms.FloatField(label='Height', required=False)
    predefined_package  = forms.CharField(label='predefined_package')
    signature = forms.CharField(label='predefined_package')

class ToAddressForm(AddressForm):
    pass

class FromAddressForm(AddressForm):
    pass



class PassphrasePrivateKeyForm(forms.Form):
    passphrase = forms.CharField(widget=forms.PasswordInput)
    private_key = forms.FileField()