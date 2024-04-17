from django.urls import path
from.import views

urlpatterns = [
    path('wallet',views.wallet,name="wallet"),
    path('razorpay_wallet_add',views.razorpay_wallet_add,name="razorpay_wallet_add"),
    path('razorpay_wallet_success',views.razorpay_wallet_success,name="razorpay_wallet_success"),
    path('handle_razorpay_wallet_success',views.handle_razorpay_wallet_success,name="handle_razorpay_wallet_success"),

    path('razorpay_wallet_payment_success',views.razorpay_wallet_payment_success,name="razorpay_wallet_payment_success"),

    path('wallet_payment_success',views.wallet_payment_success,name="wallet_payment_success"),
 
]
