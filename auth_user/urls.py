from django.urls import path,include
from . import views

urlpatterns = [
    # path('',views.home,name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('addkeys/', views.upload_keys, name='addkeys'),
    
]