from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import *
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
            return redirect('home')
    else:
        form = KeyUploadForm()
    return render(request, 'auth_user/uploadkey.html', {'form': form})







        
