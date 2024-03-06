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
    
    return redirect('create')
    return render(request, 'auth_user/home.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request,'Account was created successfully')
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
        
        try:
            user = User.objects.get(username = username )
            user = authenticate(request,username=username,password=password)
        
            if user is not None:
                login(request,user)
                return redirect('home')
            else:
                message = "Invalid Credentials"
        except:
            message= 'User does not exists'
            # messages.error(request,"User does not exists")
        
        
    context={'message':message}
    return render(request,'auth_user/login.html',context)

def user_logout(request):
    logout(request)
    return redirect('login')


def upload_keys(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        encryption = True
        return redirect('create')
    except:
        encryption = False
    if request.method == 'POST':
        # form = KeyUploadForm(request.POST, request.FILES)
        form = KeyUploadForm(request.POST)
        if form.is_valid():
            user = request.user
            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.save()
            user_profile= UserProfile.objects.get(user = request.user)
            public_key_path = user_profile.public_key_file
            shipments = Shipment.objects.filter(user = request.user)
            for shipment in shipments:
                if shipment.encryption_status == 'no':
                    to_address_instance = json.dumps(shipment.to_address['data'])
                    from_address_instance = json.dumps(shipment.from_address['data'])
                    parcel_data = json.dumps(shipment.parcel['data'])
                    shipment_id = json.dumps(shipment.shipment_id['data'])
                    
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
                   
                    shipment.to_address = to_address_info
                    shipment.from_address = from_address_info
                    shipment.parcel = parcel_instance_info
                    shipment.shipment_id = shipment_id_info
                    shipment.encryption_status = 'yes'
                    shipment.save()



            return redirect('create')
    else:
        form = KeyUploadForm()
    return render(request, 'auth_user/uploadkey.html', {'form': form,'encryption':encryption})







        
