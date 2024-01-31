from django import forms

class AddressForm(forms.Form):
    name = forms.CharField(label='Name')
    street1 = forms.CharField(label='Street 1')
    street2 = forms.CharField(label='apt/suite', required=False)
    city = forms.CharField(label='City')
    state = forms.CharField(label='State')
    zip = forms.CharField(label='ZIP Code')
    country = forms.CharField(label='Country')
    phone = forms.CharField(label='Phone', required=False)

class ParcelForm(forms.Form):
    weight = forms.FloatField(label='Weight', min_value=0)
    length = forms.FloatField(label='Length', required=False, min_value=1)
    width = forms.FloatField(label='Width', required=False, min_value=1)
    height = forms.FloatField(label='Height', required=False, min_value=1)

class Predefined_package(forms.Form):
    PREDEFINED_PACKAGE_CHOICES = [
        ('', '---------'),  # Empty choice
        ('Card', 'Card'),
        ('Letter', 'Letter'),
        ('Flat', 'Flat'),
        ('FlatRateEnvelope', 'FlatRateEnvelope'),
        ('FlatRateLegalEnvelope', 'FlatRateLegalEnvelope'),
        ('FlatRatePaddedEnvelope', 'FlatRatePaddedEnvelope'),
        ('FlatRateWindowEnvelope', 'FlatRateWindowEnvelope'),
        ('FlatRateCardboardEnvelope', 'FlatRateCardboardEnvelope'),
        ('SmallFlatRateEnvelope', 'SmallFlatRateEnvelope'),
        ('Parcel', 'Parcel'),
    ]
    predefined_package = forms.ChoiceField(label='Predefined Package', choices=PREDEFINED_PACKAGE_CHOICES,required=False,initial='')

class ToAddressForm(AddressForm):
    pass

class FromAddressForm(AddressForm):
    pass

class ShipmentForm(forms.Form):
    to_address = ToAddressForm()
    from_address = FromAddressForm()
    parcel = ParcelForm()

class PassphrasePrivateKeyForm(forms.Form):
    passphrase = forms.CharField(widget=forms.PasswordInput)
    private_key = forms.FileField()