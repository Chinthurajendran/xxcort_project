from django.urls import path
from.import views

urlpatterns = [ 
    path('coupons_info',views.coupons_info,name="coupons_info"),
    path('coupons_create',views.coupons_create,name="coupons_create"),
    path('coupons_delete,<id>',views.coupons_delete,name="coupons_delete"),
    path('coupons_edit,<id>',views.coupons_edit,name="coupons_edit"),
    path('coupons_block/<int:coupon_id>/',views.coupons_block,name="coupons_block"),

    path('checkout_coupon',views.checkout_coupon,name="checkout_coupon"),
    path('add_coupon',views.add_coupon,name="add_coupon"),
    path('coupon_create_order',views.coupon_create_order,name="coupon_create_order"),

    path('coupon_cod',views.coupon_cod,name="coupon_cod"),
    path('razorpay_payment_coupon',views.razorpay_payment_coupon,name="razorpay_payment_coupon"),
    path('coupon_payment_success',views.coupon_payment_success,name="coupon_payment_success"),
    path('coupon_razorpay_payment',views.coupon_razorpay_payment,name="coupon_razorpay_payment"),
    path('coupan_wallet_payment_success',views.coupan_wallet_payment_success,name="coupan_wallet_payment_success"),
    path('coupan_razorpay_wallet_payment_success',views.coupan_razorpay_wallet_payment_success,name="coupan_razorpay_wallet_payment_success"),

    path('payment_method_coupon',views.payment_method_coupon,name="payment_method_coupon"),

    path('generate_coupon_code/', views.generate_coupon, name='generate_coupon'),
    path('Reference_code',views.Reference_code,name="Reference_code"),

    path('wallet_point',views.wallet_point,name="wallet_point"),
]