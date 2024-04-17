from django.urls import path
from.import views

urlpatterns = [ 
    path('product_type',views.product_type,name="product_type"),
    path('product_type_delete/<id>',views.product_type_delete,name="product_type_delete"),
    path('product_type_edit/<id>',views.product_type_edit,name="product_type_edit"), 
    path('product_type_create',views.product_type_create,name="product_type_create"), 
    path('category_block_user/<int:user_id>/', views.category_block_user, name='category_block_user'),

    path('collection_sort/<id>',views.collection_sort,name="collection_sort"), 
    path('categorys',views.categorys,name="categorys"), 
]