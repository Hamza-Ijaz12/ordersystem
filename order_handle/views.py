from django.shortcuts import render,redirect
import json
import os
import requests
from .forms import *
from .models import *
from auth_user.models import *
from auth_user.utils import *
from django.contrib import messages
from django.conf import settings
# Create your views here.


def create_order(request):
    message = ''
    stored_message = messages.get_messages(request)
    if request.method == 'POST':
        to_address_form = AddressForm(request.POST, prefix='to_address')
        from_address_form = AddressForm(request.POST, prefix='from_address')
        parcel_form = ParcelForm(request.POST, prefix='parcel')
        pre_definedpackage = Predefined_package(request.POST, prefix='predefined_package')
        if to_address_form.is_valid() and from_address_form.is_valid() and parcel_form.is_valid() and pre_definedpackage.is_valid():
            print('Forms are valid')
            # print('Cleaned Data:', form.cleaned_data)
            
            to_address_data = to_address_form.cleaned_data
            from_address_data = from_address_form.cleaned_data
            parcel_data = parcel_form.cleaned_data
            to_address_data['phone'] =  str(to_address_data['phone'])
            parcel_data['weight'] =     float(parcel_data['weight'])
            if parcel_data['length']:
                parcel_data['length'] = float(parcel_data['length'])
            if parcel_data['width']:
                parcel_data['width'] = float(parcel_data['width'])
            if parcel_data['height']:
                parcel_data['height'] = float(parcel_data['height'])
            if  pre_definedpackage.cleaned_data['predefined_package'] != '':
                data = {
                    "shipment": {
                        "to_address": to_address_data,
                        "from_address": from_address_data,
                        "parcel": parcel_data,
                        'predefined_package':pre_definedpackage.cleaned_data['predefined_package']
                    }
                }
            else:
                data = {
                    "shipment": {
                        "to_address": to_address_data,
                        "from_address": from_address_data,
                        "parcel": parcel_data,
                    }
                }

            # Make EasyPost API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {'EZTKe38a8b44510e48aa8c0f641d0dacaf1buaKSuLUYlgyCTBweXDR0eg'}"
            }

            response = requests.post("https://api.easypost.com/v2/shipments", data=json.dumps(data), headers=headers)
            shipment_data = response.json()
            print(shipment_data,'==================')
            if 'created_at' in shipment_data :
                request.session['shipment_data'] = shipment_data
                if len(shipment_data['rates'])>0:
                    return redirect('confirm')
                else:
                    message = 'Unable to calculate rates'
            elif shipment_data['error']['message'] == "Invalid 'country', please provide a 2 character ISO country code.":
                    message = 'Invalid "country", please provide a 2 character ISO country code. '
            elif shipment_data['error']['message'] == 'Missing required parameter.':
                message = 'Please Check parcel details'
            elif shipment_data['error']['message'] == 'Wrong parameter type.':
                message = 'Please Check parcel details'
            else:
                
                message = shipment_data['error']['message']
        else:
            print('Forms are not valid')
            print(to_address_form.errors)
            print(from_address_form.errors)
            print(parcel_form.errors)
    else:
        to_address_form = AddressForm(prefix='to_address')
        from_address_form = AddressForm(prefix='from_address')
        parcel_form = ParcelForm(prefix='parcel')
        pre_definedpackage = Predefined_package(prefix='predefined_package')
    context = {'to_address_form': to_address_form, 'from_address_form': from_address_form, 'parcel_form': parcel_form
               ,'message':message,'pre_definedpackage':pre_definedpackage,'stored_message':stored_message}
    return render(request, 'order_handle/create.html', context)


def confirm_order(request):
    shipment_data = request.session['shipment_data']
    ratesall = shipment_data['rates']
    rates = []
    for rate in ratesall:
        if rate['service'] == 'Priority' or rate['service'] == 'GroundAdvantage' or rate['service'] == 'Express':
            rates.append(rate)
        
    if request.method =='POST':
        request.session['rate_id'] = request.POST.get('rate_id')
        return redirect('buy')
    
    context = {'shipment_data': shipment_data,'rates':rates}
    return render(request, 'order_handle/shipment_created.html', context)


def buy_order(request):
    rate_id = request.session['rate_id']
    shipment_data = request.session['shipment_data']
    

    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    # Getting that specific rate and serive
    rate_selected={}
    for rate in shipment_data['rates']:
        if rate['id'] == rate_id:
            rate_selected = rate
            break
    selected_rate_id = rate_id
    purchase_data = {
        "rate": {"id": selected_rate_id}
    }
    headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {'EZTKe38a8b44510e48aa8c0f641d0dacaf1buaKSuLUYlgyCTBweXDR0eg'}"
            }
    purchase_response = requests.post(f"https://api.easypost.com/v2/shipments/{shipment_data['id']}/buy", data=json.dumps(purchase_data), headers=headers)
    print(purchase_response.json(),'==================++++++++++')
    purchase_response_data = purchase_response.json()
    if request.user.is_authenticated:
        if 'created_at' in purchase_response_data:
            
            try:
                userprofile = UserProfile.objects.get(user=request.user)
                encryption_status = 'yes'
                public_key_path = userprofile.public_key_file.path
            except:
                encryption_status = 'no'
        
            # Creating to_address instance
            to_address_data = purchase_response_data['to_address']
            to_address_instance = {
            'name':to_address_data['name'],
            'street1':to_address_data['street1'],
            'street2':to_address_data['street2'],
            'city':to_address_data['city'],
            'state':to_address_data['state'],
            'zip':to_address_data['zip'],
            'country':to_address_data['country'],
            'phone':to_address_data['phone']
            }

            

            # Create 'from_address' instance
            from_address_data = purchase_response_data['from_address']
            from_address_instance = {
            'name':from_address_data['name'],
            'street1':from_address_data['street1'],
            'street2':from_address_data['street2'],
            'city':from_address_data['city'],
            'state':from_address_data['state'],
            'zip':from_address_data['zip'],
            'country':from_address_data['country'],
            'phone':from_address_data['phone']
            }
            
            # Create 'parcel' instance
            parcel_data = purchase_response_data['parcel']
            parcel_instance = {
            'weight':parcel_data['weight'],
            'length':parcel_data['length'],
            'width':parcel_data['width'],
            'height':parcel_data['height'],
            'predefined_package':parcel_data['predefined_package'],
            'rate' : rate_selected['rate'],
            'carrier' : rate_selected['carrier'],
            'service' : rate_selected['service']
            }
            
            shipment_id={'ship_code':purchase_response_data['id']}
            tracking_code = {'track':purchase_response_data['tracking_code']}
            # making dictonary
            if encryption_status == 'yes':
                to_address_instance = json.dumps(to_address_instance)
                from_address_instance = json.dumps(from_address_instance)
                parcel_data = json.dumps(parcel_instance)
                tracking_code = json.dumps(tracking_code)
                shipment_id = json.dumps(shipment_id)
                to_address_instance = encrypt_message(public_key_path, to_address_instance)
                from_address_instance = encrypt_message(public_key_path, from_address_instance)
                parcel_instance = encrypt_message(public_key_path, parcel_data)
                shipment_id = encrypt_message(public_key_path, shipment_id)
                tracking_code = encrypt_message(public_key_path, tracking_code)
            to_address_info={
                'data':to_address_instance
            }
            from_address_info={
                'data':from_address_instance
            }
            parcel_instance_info={
                'data':parcel_instance
            }
            shipment_id_info={
                'data':shipment_id
            }
            tracking_code_info={
                'data':tracking_code
            }
            # Create 'shipment' instance
            shipment_instance = Shipment.objects.create(
            encryption_status = encryption_status,
            shipment_id=shipment_id_info,
            tracking_code=tracking_code_info,
            user = request.user,
            to_address=to_address_info,
            from_address=from_address_info,
            parcel=parcel_instance_info
        )
    message=''
    if 'error' in purchase_response_data:
        if purchase_response_data['error']['message'] == 'The request could not be understood by the server due to malformed syntax.':
            if purchase_response_data['error']['errors'][0]['message'] == 'USState: wrong format':
                messages.error(request,'Provided states are not correct. State examples i.e NY,CA,MA')
            elif purchase_response_data['error']['errors'][0]['message'] == 'Invalid FromAddress phone number: must be 10 digits.':
                messages.error(request,'Invalid From Address phone number: must be 10 digits.')
            else:
                messages.error(request,'Provided Data is not correct kindly provide accurate Data')
            return redirect('create')
        else:
            message=purchase_response_data['error']['message']

    context = {'rate_selected':rate_selected,'shipment_data':purchase_response_data,'encryption':encryption,
               'message':message,}
    return render(request, 'order_handle/buy.html', context)

# All order lisitng view
def all_orders(request):
    message = ''
    shipments = Shipment.objects.filter(user = request.user)
    private_key_path = request.session['private_key_content']

    if 'passphrase' in request.session:
        passphrase = request.session['passphrase']
    for shipment in shipments:
        
        if shipment.encryption_status == 'yes':
            decrypted_message5 = decrypt_message(shipment.shipment_id['data'], passphrase, private_key_path)
        

            decrypted_message1 = decrypt_message(shipment.tracking_code['data'], passphrase, private_key_path)
            

            decrypted_message2 = decrypt_message(shipment.to_address['data'], passphrase, private_key_path)
            
            decrypted_message3 = decrypt_message(shipment.from_address['data'], passphrase, private_key_path)
        
            decrypted_message4 = decrypt_message(shipment.parcel['data'], passphrase, private_key_path)
            
            if decrypted_message1 == False or decrypted_message2 == False or decrypted_message3 == False or decrypted_message4 == False or decrypted_message5 == False:
                messages.error(request,"Please Check your Passpharase or Private key")
                return redirect('getpass')
            else:
                decrypted_message1 = json.loads(decrypted_message1)

                decrypted_message2 = json.loads(decrypted_message2)
                
                decrypted_message3 = json.loads(decrypted_message3)

                decrypted_message4 = json.loads(decrypted_message4)

                decrypted_message5 = json.loads(decrypted_message5)
            
            shipment.tracking_code['data'] = decrypted_message1
            shipment.to_address['data'] = decrypted_message2
            shipment.from_address['data'] = decrypted_message3
            shipment.parcel['data'] = decrypted_message4
            shipment.shipment_id['data'] = decrypted_message5

    context = {'shipments':shipments,'message':message}
    return render(request, 'order_handle/allorder.html', context)

# Details of one order
def detail_order(request,pk):
    print(pk,'-----')
    if 'passphrase' in request.session:
        passphrase = request.session['passphrase']
    shipment = Shipment.objects.get(pk=pk)
    private_key_path = request.session['private_key_content']

    if shipment.encryption_status == 'yes':
            decrypted_message5 = decrypt_message(shipment.shipment_id['data'], passphrase, private_key_path)
            

            decrypted_message1 = decrypt_message(shipment.tracking_code['data'], passphrase, private_key_path)
            

            decrypted_message2 = decrypt_message(shipment.to_address['data'], passphrase, private_key_path)
            
            decrypted_message3 = decrypt_message(shipment.from_address['data'], passphrase, private_key_path)
        
            decrypted_message4 = decrypt_message(shipment.parcel['data'], passphrase, private_key_path)
            
            decrypted_message1 = json.loads(decrypted_message1)
            decrypted_message2 = json.loads(decrypted_message2)
            decrypted_message3 = json.loads(decrypted_message3)
            decrypted_message4 = json.loads(decrypted_message4)
            decrypted_message5 = json.loads(decrypted_message5)
                
            shipment.tracking_code['data'] = decrypted_message1
            shipment.to_address['data'] = decrypted_message2
            shipment.from_address['data'] = decrypted_message3
            shipment.parcel['data'] = decrypted_message4
            shipment.shipment_id['data'] = decrypted_message5
    
    context = {'shipment':shipment}
    return render(request, 'order_handle/orderdetails.html', context)


def get_passphrase(request):
    stored_messages = messages.get_messages(request)
    stored = ''
    
    if stored_messages:
        for message in stored_messages:
            stored_messages=message
        print(stored_messages)
    if request.method == 'POST':
        form = PassphrasePrivateKeyForm(request.POST, request.FILES)
        
        if form.is_valid():
            passphrase = form.cleaned_data['passphrase']
            private_key_content = form.cleaned_data['private_key'].read().decode('utf-8')

            if not private_key_content:
                stored = 'Please provide a valid private key file.'
            else:
                # print(private_key_content)
                request.session['private_key_content'] = private_key_content
                request.session['passphrase'] = str(passphrase)
                return redirect('all')
    else:
        form = PassphrasePrivateKeyForm()     
        
    context={'stored_messages':stored_messages,'stored':stored,'form': form}
    return render(request,'order_handle/getpass.html',context)



def remove_encryption(request):
    message = ''
    if request.method == 'POST':
        passphrase = request.POST.get('passphrase')
        form = PassphrasePrivateKeyForm(request.POST, request.FILES)
        
        if form.is_valid():
            passphrase = form.cleaned_data['passphrase']
            if form.is_valid():
                passphrase = form.cleaned_data['passphrase']
                private_key_content = form.cleaned_data['private_key'].read().decode('utf-8')

                if not private_key_content:
                    stored = 'Please provide a valid private key file.'
                 
        
            private_key_path = private_key_content

        
            print('--------', passphrase)
            shipments = Shipment.objects.filter(user = request.user)
            total = len(shipments)
            count = 0
            for shipment in shipments:
                if shipment.encryption_status == 'yes':
                    decrypted_message5 = decrypt_message(shipment.shipment_id['data'], passphrase, private_key_path)

                    decrypted_message1 = decrypt_message(shipment.tracking_code['data'], passphrase, private_key_path)

                    decrypted_message2 = decrypt_message(shipment.to_address['data'], passphrase, private_key_path)
                    
                    decrypted_message3 = decrypt_message(shipment.from_address['data'], passphrase, private_key_path)
                
                    decrypted_message4 = decrypt_message(shipment.parcel['data'], passphrase, private_key_path)
                    
                    if decrypted_message1 == False or decrypted_message2 == False or decrypted_message3 == False or decrypted_message4 == False or decrypted_message5 == False:
                        message = "Please Check your Passpharase or Private key"
                        break
                    else:
                        decrypted_message1 = json.loads(decrypted_message1)

                        decrypted_message2 = json.loads(decrypted_message2)
                        
                        decrypted_message3 = json.loads(decrypted_message3)

                        decrypted_message4 = json.loads(decrypted_message4)

                        decrypted_message5 = json.loads(decrypted_message5)
                
                    shipment.tracking_code['data'] = decrypted_message1
                    shipment.to_address['data'] = decrypted_message2
                    shipment.from_address['data'] = decrypted_message3
                    shipment.parcel['data'] = decrypted_message4
                    shipment.shipment_id['data'] = decrypted_message5
                    shipment.encryption_status = 'no'
                    shipment.save()
            for shipment in shipments:
                if shipment.encryption_status == 'no':
                    count = count+1
            if total == count:
                userprofile = UserProfile.objects.get(user = request.user)
                userprofile.delete()
                if 'private_key_content' in request.session:
                    del request.session['private_key_content']
                if 'passphrase' in request.session:
                    del request.session['passphrase']
                return redirect('home')
    else:
        form = PassphrasePrivateKeyForm()  


            
    context={'message':message,'form':form}
    return render(request,'order_handle/remove_encrypt.html',context)