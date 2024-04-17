from django.urls import path
from.import views

urlpatterns = [ 
    path('admin_product_info',views.admin_product_info,name="admin_product_info"),
    path('admin_product_info_create',views.admin_product_info_create,name="admin_product_info_create"),
    path('admin_product_info_delete/<id>',views.admin_product_info_delete,name="admin_product_info_delete"),
    path('admin_product_info_edit/<id>',views.admin_product_info_edit,name="admin_product_info_edit"),
    path('products_block_user/<int:user_id>/', views.products_block_user, name='products_block_user'),
]