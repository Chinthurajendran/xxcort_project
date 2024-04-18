from django.urls import path
from.import views

urlpatterns = [
    path('admin_index',views.index,name="admin_index"), 
    path('admin',views.admin_login,name="admin_login"), 
    path('admin_logout',views.admin_logout,name="admin_logout"), 
    path('admin_user_info',views.admin_user_info,name="admin_user_info"),
    path('admin_user_info_edit/<id>',views.admin_user_info_edit,name="admin_user_info_edit"),
    path('admin_delete/<id>',views.admin_delete,name="admin_delete"),
    path('admin_search',views.admin_search,name="admin_search"),
    path('admin_user_info_create',views.admin_user_info_create,name="admin_user_info_create"),
    path('order_list', views.new_order_list, name='order_list'),

    path('new_order_approval_list', views.new_order_approval_list, name='new_order_approval_list'),
    path('admin_order_cancel/<id>', views.admin_order_cancel, name='admin_order_cancel'),
    path('admin_refund/<id>', views.admin_refund, name='admin_refund'),
    path("change_status/<id>",views.change_status,name="change_status"),

    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path("change_status/<id>",views.change_status,name="change_status"),

    path("order_denied/<id>",views.order_denied,name="order_denied"),

    path('admin_order_in_detail/<id>',views.admin_order_in_detail,name="admin_order_in_detail"),

    
]