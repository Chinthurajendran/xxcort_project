from django.urls import path
from.import views
from coupons.views import generate_coupon

urlpatterns = [ 
    path('check_out',views.check_out,name="check_out"), 

    path('place_order',views.place_order,name="place_order"),
    path('payment_selection',views.payment_selection,name="payment_selection"),
    path('cod',views.cod,name="cod"),
    path('razorpay_payment',views.razorpay_payment,name='razorpay_payment'),
    path('handle_razorpay_success', views.handle_razorpay_success, name='handle_razorpay_success'),
    path('razorpay_payment_success', views.razorpay_payment_success, name='razorpay_payment_success'),
    path('check_out_success',views.check_out_success,name="check_out_success"),
    path('razorpay_success',views.razorpay_success,name="razorpay_success"),
    path('coupan_offers',views.coupan_offers,name="coupan_offers"),

    path('order_in_detail/<id>',views.order_in_detail,name="order_in_detail"),

    path('generate_coupon/', generate_coupon, name='generate_coupon_code'),
    
]