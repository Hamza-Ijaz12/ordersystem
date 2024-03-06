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
from django.http import JsonResponse , HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .config import *
import urllib.parse
import hmac
import hashlib
from django.core.mail import send_mail
from django.conf import settings
# for US states
import us

# Create your views here.

# Payment gateway funtioncs for easier handling
# creating hmac (required for header api demand) and also making params according to required formate
def create_hmac(params):
    """ Generate an HMAC based upon the raw post data parameters """
    raw_post_data = '&'.join([f'{key}={value}' for key, value in sorted(params.items())])
    encoded = raw_post_data.encode('utf-8')
    private_key = coinpay_privatekey  # Replace with your actual private key
    return raw_post_data, hmac.new(bytearray(private_key, 'utf-8'), encoded, hashlib.sha512).hexdigest()

# Calling gateway
def gatewayapicall(payload):
    coinremitter_api_url = 'https://www.coinpayments.net/api.php'

    

    encoded, sig = create_hmac(payload)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'hmac': sig,
    }

    respay = requests.post(coinremitter_api_url, data=encoded, headers=headers)
    return respay.json()

# PAyment gateway function end

def create_order(request):
    states = us.states.STATES
    if 'payment_status' in request.session:
        del request.session['payment_status']
    
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
            print(to_address_form.errors,'to')

            print(from_address_form.errors,'from')
            print(parcel_form.errors)
    else:
        to_address_form = AddressForm(prefix='to_address')
        from_address_form = AddressForm(prefix='from_address')
        parcel_form = ParcelForm(prefix='parcel')
        
    context = {'to_address_form': to_address_form, 'from_address_form': from_address_form, 'parcel_form': parcel_form
               ,'message':message,'stored_message':stored_message,'encryption':encryption,'states':states}
    return render(request, 'order_handle/index.html', context)


def confirm_order(request):
    if 'transaction_id' in request.session:
        del request.session['transaction_id']
    if 'payment_status' in request.session:
        del request.session['payment_status']
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    proceesing_fee =  Processing_Fee.objects.first()
    shipment_data = request.session['shipment_data']
    ratesall = shipment_data['rates']
    rates = []
    for rate in ratesall:
        if rate['service'] == 'Priority' or rate['service'] == 'GroundAdvantage' or rate['service'] == 'Express':
            processing_fee_toadd = round(float(rate['rate']) * (proceesing_fee.fee/100), 2)
            total = processing_fee_toadd + float(rate['rate'])
            dic = {'rate':rate,'total':total}
            rates.append(dic)
        
    if request.method =='POST':
        request.session['rate_id'] = request.POST.get('rate_id')
        return redirect('payment')
    
    context = {'shipment_data': shipment_data,'rates':rates}
    return render(request, 'order_handle/confirm.html', context)



# Payment view where payment reciving info will be shown
def get_payment(request):
    coin = ''
    message = ''
    rate_id = request.session['rate_id']
    shipment_data = request.session['shipment_data']
    proceesing_fee =  Processing_Fee.objects.first()
    if not proceesing_fee:
        proceesing_fee = 0
    rate_selected={}
    for rate in shipment_data['rates']:
        if rate['id'] == rate_id:
            rate_selected = rate
            break
    processing_fee_toadd = round(float(rate_selected['rate']) * (proceesing_fee.fee/100), 2)

    ready_to_pay = False
    # Checking status of transaction
    if 'transaction_id' in request.session:
        request.session['transaction_id']
        print('trans_id',request.session['transaction_id'])
        print('trans check')
        payload = {
        'version': 1,
        'key': coinpay_public,
        'cmd': 'get_tx_info',
        'txid' : request.session['transaction_id']
        }
        try:
            response = gatewayapicall(payload)
        except:
            return redirect('payment')
        print(response)
        if response['error'] == 'ok':
            if response['result']['status'] >= 100 or response['result']['status'] >= 2:
                
                request.session['payment_status'] = True
                return redirect('buy')
            else:
                request.session['payment_status'] = False

        else:
            message = 'Something went wrong with tranaction checking'
    else:
        print('no iID')


    datapay={}
    if request.method == 'POST':
        
        email = request.POST.get('email')
        coin = request.POST.get('coin')
        request.session['coin_name'] = coin
        # makeing Payment_handle model instance so that upon payment confirmation webhook send tracking code to email of user
        # Payment gateway
        payload = {
            'version': 1,
            'key': coinpay_public,
            'cmd': 'create_transaction',
            'amount' : float(rate_selected['rate'])+processing_fee_toadd,
            'currency1' : 'USD',
            'currency2' : coin,
            'buyer_email'  : email
        }
        try:
    
            datapay = gatewayapicall(payload)
        except:
            return redirect('payment')
        print(datapay)
        # Payment gateway end
        if datapay['error'] == 'ok':
            transaction_id = datapay['result']['txn_id']
            print('before setting', transaction_id)
            request.session['transaction_id'] = transaction_id
            print('after setting',request.session['transaction_id'])
            ready_to_pay = True
            if request.user.is_authenticated:
                Payment_handle.objects.create(
                    shipment_id = shipment_data['id'],
                    user = request.user,
                    rate_id = rate_id,
                    transaction_id = transaction_id,
                    status = 'Pending'
                )
            else:
                Payment_handle.objects.create(
                    shipment_id = shipment_data['id'],
                    rate_id = rate_id,
                    transaction_id = transaction_id,
                    status = 'Pending'
                )
        else:
            message = datapay['error']
    # Process the response and return payment details to the frontend

   
    
    
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
   
    total = processing_fee_toadd + float(rate_selected['rate'])
    context = {'rate_selected':rate_selected,'encryption':encryption,'processing_fee_toadd':processing_fee_toadd,
               'message':message,'datapay':datapay,'ready_to_pay':ready_to_pay,'total':total,'coin':coin}
    return render(request, 'order_handle/payment.html', context)

# Buying shipment
def buy_order(request):
    
    if 'payment_status' in request.session:
        
        if request.session['payment_status']:
            coin = request.session['coin_name']
            rate_id = request.session['rate_id']
            shipment_data = request.session['shipment_data']
            proceesing_fee = Processing_Fee.objects.first()
            print(proceesing_fee.fee,'----------------')
            if not proceesing_fee.fee:
                proceesing_fee.fee = 0
            
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
            processing_fee_toadd = round(float(rate_selected['rate']) * (proceesing_fee.fee/100), 2)
            total = processing_fee_toadd + float(rate_selected['rate'])
            headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {'EZTKe38a8b44510e48aa8c0f641d0dacaf1buaKSuLUYlgyCTBweXDR0eg'}"
                    }
            purchase_response = requests.post(f"https://api.easypost.com/v2/shipments/{shipment_data['id']}/buy", data=json.dumps(purchase_data), headers=headers)
            print(purchase_response.json(),'==================++++++++++')
            purchase_response_data = purchase_response.json()

            
            if 'error' in purchase_response_data:
               if purchase_response_data['error']['message'] == 'Postage already exists for this shipment.':
                    # getting shipment from easypost
                    response = requests.get(f"{base_url}/shipments/{shipment_data['id']}", headers=headers)
                    if response.status_code == 200:
                        # handling of shipment create if there is user
                        purchase_response_data = response.json()
            # setting payment_handle update model here
            transaction_d = request.session['transaction_id']
            payment_handle_inst = Payment_handle.objects.get(transaction_id = transaction_d)
            payment_handle_inst.status = 'done'
            payment_handle_inst.tracking_code = purchase_response_data['tracking_code']
            payment_handle_inst.save()
                
            if request.user.is_authenticated:
                if 'created_at' in purchase_response_data:
                    processing_fee_toadd = round(float(rate_selected['rate']) * (proceesing_fee.fee/100), 2)
                    
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
                    'rate' : float(rate_selected['rate']) + processing_fee_toadd,
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
                    
                    # Payment handle shipment status handle here so that if shipment is already bought it is not done again
                    
                    if 'transaction_id' in request.session:
                        del request.session['transaction_id']
                    if 'payment_status' in request.session:
                        del request.session['payment_status']
                     
                    # 17 Track API calling
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
                elif purchase_response_data['error']['message'] == 'Postage already exists for this shipment.':
                    # getting shipment from easypost
                    response = requests.get(f"{base_url}/shipments/{shipment_data['id']}", headers=headers)
                    if response.status_code == 200:
                        # handling of shipment create if there is user
                        purchase_response_data = response.json()
                        
                else:
                    message=purchase_response_data['error']['message']
            
            context = {'rate_selected':rate_selected,'shipment_data':purchase_response_data,'encryption':encryption,
                    'message':message,'coin':coin,'total':total}
            return render(request, 'order_handle/buy.html', context)
        else:
            return redirect('create')
    else:
        return redirect('create')




# All order lisitng view
def all_orders(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False
    message = ''
    shipments = Shipment.objects.filter(user = request.user)
    

    

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
    
    shipment = Shipment.objects.get(pk=pk)
    
    
    context = {'shipment':shipment,'encryption':encryption}
    return render(request, 'order_handle/orderdetails.html', context)


def get_processingfee(request):
    if request.user.is_staff:
        try:
            userprofile = UserProfile.objects.get(user=request.user)
            encryption = True
        except:
            encryption = False

        fees = Processing_Fee.objects.first()

        if request.method == 'POST':
            processing_fee = request.POST.get('processing_fee')
            if fees:
                print('----------------------')
                print('fee type',type(fees))
                print('get type',type(processing_fee))
                fees.fee = processing_fee
                fees.save()
            else:
                Processing_Fee.objects.create(
                    fee = processing_fee
                )
            print(processing_fee,'feeeeee')
            context={'encryption':encryption,'fee':fees}
            return render(request,'order_handle/get_fee.html',context)
        
        
            
        context={'encryption':encryption,'fee':fees}
        return render(request,'order_handle/get_fee.html',context)
    else:
        return redirect('create')



def remove_encryption(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        userprofile.delete()
        encryption = True
    except:
        encryption = False

    return redirect('create')


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




# 17tracks Webhook handling
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
    

# coinpayment IPN/Webhook handling
@csrf_exempt
@require_POST
def webhook_ipn_handle(request):
    try:
       
        # from config.py file both merchat_id and IPN secrect key
        merchant_id = merchant_id_c
        secret = IPN_secrect_key
        print('entered webhook')
        # Ensure HMAC signature is sent
        if 'HTTP_HMAC' not in request.META or not request.META['HTTP_HMAC']:
            return HttpResponseBadRequest("No HMAC signature sent")

        print('check1')
        # Get merchant ID from POST data
        merchant = request.POST.get('merchant', '')
        if not merchant:
            return HttpResponseBadRequest("No Merchant ID passed")
        print('check2')

        # Validate Merchant ID
        if merchant != merchant_id:
            return HttpResponseBadRequest("Invalid Merchant ID")

        print('check3_merchat')
        # Read POST data
        request_data = request.body.decode('utf-8')
        if not request_data:
            return HttpResponseBadRequest("Error reading POST data")
        print('check4')

        # Calculate HMAC signature
        calculated_hmac = hmac.new(secret.encode('utf-8'), request_data.encode('utf-8'), hashlib.sha512).hexdigest()

        # Validate HMAC signature
        if calculated_hmac != request.META['HTTP_HMAC']:
            return HttpResponseBadRequest("HMAC signature does not match")
        print('check5')

        # Process IPN here
        print('webhook received and worked')
        txn_id = request.POST.get('txn_id')
        ipn_type = request.POST.get('ipn_type')
        print('txn_id',txn_id)
        status = int(request.POST.get('status', 0))
        print('status',status)
        email = request.POST.get('email')
        print('email',email)
        if (status == 2 or status >=100) and ipn_type == 'api':
            print('handle email logic here')
            payment_handle_inst = Payment_handle.objects.get(transaction_id = txn_id)
            print(payment_handle_inst.status,'status')
            if payment_handle_inst.status == 'done':
                print('payment was done and only email sent')
                tracking_code = payment_handle_inst.tracking_code

                
                customer_email = email

                # Your logic to send an email with the tracking code
                subject = 'Your Order Tracking Code'
                message = f'Thank you for your purchase! Your tracking code is: {tracking_code}'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [customer_email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                payment_handle_inst.delete()

                return HttpResponse('Email sent successfully')
            else:
                shipment_id = payment_handle_inst.shipment_id
                rate_id = payment_handle_inst.rate_id
                # getting shipment from easypost
                response = requests.get(f"{base_url}/shipments/{shipment_id}", headers=headers)
                if response.status_code == 200:
                    # handling of shipment create if there is user
                    shipment_data = response.json()

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
                    
                    purchase_response = requests.post(f"{base_url}/shipments/{shipment_data['id']}/buy", data=json.dumps(purchase_data), headers=headers)
                    print(purchase_response.json(),'==================++++++++++')
                    purchase_response_data = purchase_response.json()
                    if 'created_at' in purchase_response_data:
                        tracking_code = purchase_response_data['tracking_code']
                        if payment_handle_inst.user:
                            print('payment was pending and shipment bought and user history set')
                            proceesing_fee = Processing_Fee.objects.first()
                            if not proceesing_fee:
                                proceesing_fee = 0
                            proceesing_fee_toadd = round(float(rate_selected['rate']) * (proceesing_fee.fee/100), 2)
                            try:
                                userprofile = UserProfile.objects.get(user = payment_handle_inst.user)
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
                            'rate' : float(rate_selected['rate']) + proceesing_fee_toadd ,
                            'carrier' : rate_selected['carrier'],
                            'service' : rate_selected['service']
                            }
                            
                            shipment_id={'ship_code':purchase_response_data['id']}
                            
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
                            user = payment_handle_inst.user,
                            to_address=to_address_info,
                            from_address=from_address_info,
                            parcel=parcel_instance_info
                            )  
                            payment_handle_inst.delete()
                        else:
                            print('payment was pending and shipment bought and email')
                            customer_email = email

                            # Your logic to send an email with the tracking code
                            subject = 'Your Order Tracking Code'
                            message = f'Thank you for your purchase! Your tracking code is: {tracking_code}'
                            from_email = settings.EMAIL_HOST_USER
                            recipient_list = [customer_email]

                            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                            payment_handle_inst.delete()

                            return HttpResponse('Email sent successfully')
                





    

        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError as e:
        print('error',e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)