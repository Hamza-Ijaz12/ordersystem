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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# Create your views here.


def create_order(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    message = ''
    stored_message = messages.get_messages(request)
    if request.method == 'POST':
        to_address_form = AddressForm(request.POST, prefix='to_address')
        from_address_form = AddressForm(request.POST, prefix='from_address')
        parcel_form = ParcelForm(request.POST, prefix='parcel')
        if to_address_form.is_valid() and from_address_form.is_valid() and parcel_form.is_valid() :
            print('Forms are valid')
            # print('Cleaned Data:', form.cleaned_data)
            
            to_address_data = to_address_form.cleaned_data
            from_address_data = from_address_form.cleaned_data
            parcel_data = parcel_form.cleaned_data
            to_address_data['phone'] =  str(to_address_data['phone'])
            parcel_data['weight_lb'] =     float(parcel_data['weight_lb'])
            parcel_data['weight_oz'] =     float(parcel_data['weight_oz'])
            if parcel_data['length']:
                parcel_data['length'] = float(parcel_data['length'])
            if parcel_data['width']:
                parcel_data['width'] = float(parcel_data['width'])
            if parcel_data['height']:
                parcel_data['height'] = float(parcel_data['height'])
            print('parcel data ====== ',parcel_data)
            if parcel_data['predefined_package'] == 'custom':
                if parcel_data['length']== None or parcel_data['width']== None or parcel_data['height']== None:
                    message = 'Kindly provide length,width and height for Custom pacakge'
                    parcel_info = {'weight':(parcel_data['weight_lb']*16) + (parcel_data['weight_oz']) , 'length': parcel_data['length'], 'width': parcel_data['width'], 'height': parcel_data['width'], 'predefined_package': parcel_data['predefined_package']}
                else:
                    parcel_info = {'weight':(parcel_data['weight_lb']*16) + (parcel_data['weight_oz']) , 'length': parcel_data['length'], 'width': parcel_data['width'], 'height': parcel_data['width']}

            else:
                parcel_info = {'weight':(parcel_data['weight_lb']*16) + (parcel_data['weight_oz']) , 'length': parcel_data['length'], 'width': parcel_data['width'], 'height': parcel_data['width'], 'predefined_package': parcel_data['predefined_package']}
            
            data = {
                "shipment": {
                    "to_address": to_address_data,
                    "from_address": from_address_data,
                    "parcel": parcel_info,
                    "options":{
                        'delivery_confirmation':parcel_data['signature']
                    }
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
                elif len(message)<=0:   
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
        
    context = {'to_address_form': to_address_form, 'from_address_form': from_address_form, 'parcel_form': parcel_form
               ,'message':message,'stored_message':stored_message,'encryption':encryption}
    return render(request, 'order_handle/index.html', context)


def confirm_order(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
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
    return render(request, 'order_handle/confirm.html', context)


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
            tracking_code = purchase_response_data['tracking_code']
            # making dictonary
            if encryption_status == 'yes':
                to_address_instance = json.dumps(to_address_instance)
                from_address_instance = json.dumps(from_address_instance)
                parcel_data = json.dumps(parcel_instance)
                
                shipment_id = json.dumps(shipment_id)
                to_address_instance = encrypt_message(public_key_path, to_address_instance)
                from_address_instance = encrypt_message(public_key_path, from_address_instance)
                parcel_instance = encrypt_message(public_key_path, parcel_data)
                shipment_id = encrypt_message(public_key_path, shipment_id)
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
            
            
            # Create 'shipment' instance
            shipment_instance = Shipment.objects.create(
            encryption_status = encryption_status,
            shipment_id=shipment_id_info,
            tracking_code=tracking_code,
            user = request.user,
            to_address=to_address_info,
            from_address=from_address_info,
            parcel=parcel_instance_info
        )   
            
            data = [
                {
                    "number": purchase_response_data['tracking_code']
                }
            ]
            headers = {
                            '17token': '10D4C571303DF9956AF2265600AC2AD4',
                            'Content-Type': 'application/json'
                        }
            response = requests.post(url = "https://api.17track.net/track/v2.2/register", headers=headers, json=data)
            print('---------',response.json())
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
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    message = ''
    shipments = Shipment.objects.filter(user = request.user)
    if 'private_key_content' in request.session:
        private_key_path = request.session['private_key_content']

    if 'passphrase' in request.session:
        passphrase = request.session['passphrase']
    for shipment in shipments:
        
        if shipment.encryption_status == 'yes':
            decrypted_message5 = decrypt_message(shipment.shipment_id['data'], passphrase, private_key_path)

            decrypted_message2 = decrypt_message(shipment.to_address['data'], passphrase, private_key_path)
            
            decrypted_message3 = decrypt_message(shipment.from_address['data'], passphrase, private_key_path)
        
            decrypted_message4 = decrypt_message(shipment.parcel['data'], passphrase, private_key_path)
            
            if  decrypted_message2 == False or decrypted_message3 == False or decrypted_message4 == False or decrypted_message5 == False:
                messages.error(request,"Please Check your Passpharase or Private key")
                return redirect('getpass')
            if  decrypted_message2 == 'Error importing public key' or decrypted_message3 == 'Error importing public key' or decrypted_message4 == 'Error importing public key' or decrypted_message5 == 'Error importing public key':
                message = "Please Check your Private key"
                return redirect('getpass')
            else:
               

                decrypted_message2 = json.loads(decrypted_message2)
                
                decrypted_message3 = json.loads(decrypted_message3)

                decrypted_message4 = json.loads(decrypted_message4)

                decrypted_message5 = json.loads(decrypted_message5)
            
            
            shipment.to_address['data'] = decrypted_message2
            shipment.from_address['data'] = decrypted_message3
            shipment.parcel['data'] = decrypted_message4
            shipment.shipment_id['data'] = decrypted_message5

    context = {'shipments':shipments,'message':message,'encryption':encryption}
    return render(request, 'order_handle/allorder.html', context)







# Details of one order
def detail_order(request,pk):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    print(pk,'-----')
    if 'passphrase' in request.session:
        passphrase = request.session['passphrase']
    shipment = Shipment.objects.get(pk=pk)
    if 'private_key_content' in request.session:
        private_key_path = request.session['private_key_content']

    if shipment.encryption_status == 'yes':
            decrypted_message5 = decrypt_message(shipment.shipment_id['data'], passphrase, private_key_path)

            decrypted_message2 = decrypt_message(shipment.to_address['data'], passphrase, private_key_path)
            
            decrypted_message3 = decrypt_message(shipment.from_address['data'], passphrase, private_key_path)
        
            decrypted_message4 = decrypt_message(shipment.parcel['data'], passphrase, private_key_path)
            
            decrypted_message2 = json.loads(decrypted_message2)
            decrypted_message3 = json.loads(decrypted_message3)
            decrypted_message4 = json.loads(decrypted_message4)
            decrypted_message5 = json.loads(decrypted_message5)
                
            shipment.to_address['data'] = decrypted_message2
            shipment.from_address['data'] = decrypted_message3
            shipment.parcel['data'] = decrypted_message4
            shipment.shipment_id['data'] = decrypted_message5
    
    context = {'shipment':shipment,'encryption':encryption}
    return render(request, 'order_handle/orderdetails.html', context)


def get_passphrase(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
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
        
    context={'stored_messages':stored_messages,'stored':stored,'form': form,'encryption':encryption}
    return render(request,'order_handle/getpass.html',context)



def remove_encryption(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    message = ''
    if request.method == 'POST':
        form = PassphrasePrivateKeyForm(request.POST, request.FILES)
        
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

                    decrypted_message2 = decrypt_message(shipment.to_address['data'], passphrase, private_key_path)
                    
                    decrypted_message3 = decrypt_message(shipment.from_address['data'], passphrase, private_key_path)
                
                    decrypted_message4 = decrypt_message(shipment.parcel['data'], passphrase, private_key_path)
                    
                    if decrypted_message2 == False or decrypted_message3 == False or decrypted_message4 == False or decrypted_message5 == False:
                        message = "Please Check your Passpharase or Private key"
                        break
                    if decrypted_message2 == 'Error importing public key' or decrypted_message3 == 'Error importing public key' or decrypted_message4 == 'Error importing public key' or decrypted_message5 == 'Error importing public key':
                        message = "Please Check your Private key"
                        break
                    else:
                        decrypted_message2 = json.loads(decrypted_message2)
                        
                        decrypted_message3 = json.loads(decrypted_message3)

                        decrypted_message4 = json.loads(decrypted_message4)

                        decrypted_message5 = json.loads(decrypted_message5)
                
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
                return redirect('create')
    else:
        form = PassphrasePrivateKeyForm()  


            
    context={'message':message,'form':form,'encryption':encryption}
    return render(request,'order_handle/remove_encrypt.html',context)


# Tracking handle
def tracking_handle(request):
    if request.method == 'POST':
        # Set headers for EasyPost API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {'EZTKe38a8b44510e48aa8c0f641d0dacaf1buaKSuLUYlgyCTBweXDR0eg'}"
        }
        try:
            # Get tracking code from the request
            tracking_code = request.POST.get('tracking')

            # Check if an existing Tracker with the same tracking code exists
            existing_tracker_response = requests.get(f"https://api.easypost.com/v2/trackers?tracking_code={tracking_code}", headers=headers)
            existing_tracker = existing_tracker_response.json()
            print('existing_tracker',existing_tracker)
            if existing_tracker:
                if len(existing_tracker['trackers'])>0:
                    # If an existing Tracker is found, return its information
                    data = True
                    tracking_code = existing_tracker['trackers'][0]['tracking_code']
                    status = existing_tracker['trackers'][0]['status']
                    est_delivery_date = existing_tracker['trackers'][0]['est_delivery_date']
                    date = est_delivery_date.split('T')[0] if est_delivery_date else ''
                    context = {'tracking_code': tracking_code, 'status': status, 'date': date, 'data': data}
                    return render(request, 'order_handle/tracking.html', context)
            else:
                print('her3')
                error = existing_tracker['error']['message']
                print('Error is ', error)
                context = {}

            # Make EasyPost API request to create a new Tracker
            tracker_data = {"tracking_code": tracking_code}
            tracker_response = requests.post("https://api.easypost.com/v2/trackers", data=json.dumps({"tracker": tracker_data}), headers=headers)
            print(tracker_response.json(), '===============')
            tracking_data = tracker_response.json()
            print('her1')

            if tracking_data:
                print('her2')
                data = True
                tracking_code = tracking_data['tracking_code']
                status = tracking_data['status']
                est_delivery_date = tracking_data.get('est_delivery_date', '')
                date = est_delivery_date.split('T')[0] if est_delivery_date else ''
                context = {'tracking_code': tracking_code, 'status': status, 'date': date, 'data': data}
            else:
                print('her3')
                error = tracking_data['error']['message']
                print('Error is ', error)
                context = {}
        except Exception as e:
            print('Something went wrong:', str(e))
            message = 'Something went wrong'
            context = {'message': message}
    else:
        context = {}

    return render(request, 'order_handle/tracking.html', context)




# Webhook handling
@csrf_exempt
@require_POST
def webhook_handle(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        print('Webhook Payload:', payload)  # Print the payload for debugging

        # Extract relevant information from the payload
        event_type = payload['event']
        if event_type == 'TRACKING_UPDATED':
            tracking_code = payload['data']['number']
            try:
                shipment = Shipment.objects.get(tracking_code = tracking_code)
                print('here1')
                print(shipment)
                print('========',payload['data']['track_info']['latest_status'])
                sub_status = payload['data']['track_info']['latest_status']['sub_status']
                main_status = payload['data']['track_info']['latest_status']['status']
                print('here2')
                if sub_status == 'NotFound_Other' or sub_status == 'NotFound_InvalidCode':
                    status = 'Tracking number not found for this package'
                    print('here3')
                    shipment.sub_status = sub_status
                    shipment.main_status = main_status
                    shipment.save()
                else:
                    print('here4')
                    shipment.sub_status=sub_status
                    shipment.main_status=main_status
                    shipment.save()
                print('-------',status)
            except:
                print('tracking code does not exsists')


        

        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)