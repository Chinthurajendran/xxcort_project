from django.urls import path
from.import views

urlpatterns = [ 
    path('cart_create/<id>',views.cart_create,name="cart_create"),
    path('cart_delete/<id>',views.cart_delete,name="cart_delete"),
    
    path('cart/', views.cart, name='cart'),
    path('update-cart-item/', views.update_cart_item, name='update_cart_item'),

    path('cart_view',views.cart_view,name="cart_view"),
   
]