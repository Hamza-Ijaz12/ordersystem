from django.urls import path,include
from . import views

urlpatterns = [
    # path('',views.home,name='home'),
    path('create/', views.create_order, name='create'),
    path('conftm/', views.confirm_order, name='confirm'),
    path('buy/', views.buy_order, name='buy'),
    path('payment/', views.get_payment, name='payment'),
    path('all/', views.all_orders, name='all'),
    path('processing_fee/', views.get_processingfee, name='processing_fee'),
    path('removeenc/', views.remove_encryption, name='remove'),
    path('tracking/', views.tracking_handle, name='tracking'),
    path('detail/<str:pk>', views.detail_order, name='detail'),
   
#    for 17tracks 
    path('webhook/', views.webhook_handle, name='webhook'),
    # for IPN/Webhook of coinpayment gateway
    path('webhook_ipn/', views.webhook_ipn_handle, name='webhook_ipn'),


    
]