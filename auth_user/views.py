from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import *
from order_handle.models import Shipment
import json




def home(request):
    stored_messages = messages.get_messages(request)
    
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
    except:
        encryption = False


    for message in stored_messages:
        print(message,'----------------')
    context = {'stored_messages':stored_messages,'encryption':encryption,
               }
    return render(request, 'auth_user/home.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            context = {'form': form}
            return redirect('home')
    else:
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'auth_user/signup.html', context)



def loginpage(request):
    message = ''
    if request.method =="POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        print('========',username)
        print('========',password)
        try:
            user = User.objects.get(username = username )
            user = authenticate(request,username=username,password=password)
        
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                message = "credentials Invalid"
        except:
            message= 'User does not exists'
            # messages.error(request,"User does not exists")
        
        
    context={'message':message}
    return render(request,'auth_user/login.html',context)

def user_logout(request):
    logout(request)
    return redirect('login')


def upload_keys(request):
    if request.method == 'POST':
        form = KeyUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.save()
            user_profile= UserProfile.objects.get(user = request.user)
            public_key_path = user_profile.public_key_file.path
            shipments = Shipment.objects.filter(user = request.user)
            for shipment in shipments:
                if shipment.encryption_status == 'no':
                    to_address_instance = json.dumps(shipment.to_address['data'])
                    from_address_instance = json.dumps(shipment.from_address['data'])
                    parcel_data = json.dumps(shipment.parcel['data'])
                    shipment_id = json.dumps(shipment.shipment_id['data'])
                    tracking_code = json.dumps(shipment.tracking_code['data'])
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
                    shipment.to_address = to_address_info
                    shipment.from_address = from_address_info
                    shipment.parcel = parcel_instance_info
                    shipment.shipment_id = shipment_id_info
                    shipment.tracking_code = tracking_code_info
                    shipment.encryption_status = 'yes'
                    shipment.save()



            return redirect('home')
    else:
        form = KeyUploadForm()
    return render(request, 'auth_user/uploadkey.html', {'form': form})







        
