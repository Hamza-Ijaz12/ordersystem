from django.urls import path,include
from . import views

urlpatterns = [
    # path('',views.home,name='home'),
    path('create/', views.create_order, name='create'),
    path('conftm/', views.confirm_order, name='confirm'),
    path('buy/', views.buy_order, name='buy'),
    path('all/', views.all_orders, name='all'),
    path('getpass/', views.get_passphrase, name='getpass'),
    path('detail/<str:pk>', views.detail_order, name='detail'),
   
    
]