from django.urls import path
from.import views

urlpatterns = [
    path('',views.index,name="index"),
    path('index', views.index, name='index'),


    path('login',views.login,name="login"),
    path('signup',views.signup,name="signup"),
    path('logout',views.logout,name="logout"),
    path('forgot_password',views.forgot_password,name="forgot_password"),

    path('send_otp',views.send_otp,name="send_otp"),
    path('verification',views.verification,name="verification"),
    path('resend_otp',views.resend_otp,name="resend_otp"),
    path('user_profile',views.user_profile,name="user_profile"),

    path('accounts/google/login/callback',views.google_oauth_callback,name="google_oauth_callback"),

    path('user_index',views.user_index,name="user_index"),
    path('user_profile',views.user_profile,name="user_profile"),
    path('user_profile_change_password_edit',views.user_profile_change_password_edit,name="user_profile_change_password_edit"),
    path('user_profile_edits',views.user_profile_edits,name="user_profile_edits"),
    path('user_profile_address',views.user_profile_address,name="user_profile_address"),
    path('user_profile_address_create',views.user_profile_address_create,name="user_profile_address_create"),
    path('user_profile_address_edit/<id>',views.user_profile_address_edit,name="user_profile_address_edit"),
    path('user_profile_address_delete/<id>',views.user_profile_address_delete,name="user_profile_address_delete"),
    path('sec_user_profile_address',views.sec_user_profile_address,name="sec_user_profile_address"),
    path('sec_user_profile_address_edit/<id>',views.sec_user_profile_address_edit,name="sec_user_profile_address_edit"),
    path('sec_user_profile_address_create',views.sec_user_profile_address_create,name="sec_user_profile_address_create"),
    path('sec_user_profile_address_delete/<id>',views.sec_user_profile_address_delete,name="sec_user_profile_address_delete"),
    path('order_details',views.order_details,name="order_details"),
    path('order_cancel/<id>',views.order_cancel,name="order_cancel"),
    path('refund/<id>',views.refund,name="refund"),

    path('search',views.search,name="search"),

    path('submit-cancellation-reason/<id>', views.submit_cancellation_reason, name='submit_cancellation_reason'),

]
