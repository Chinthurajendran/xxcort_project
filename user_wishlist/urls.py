from django.urls import path
from.import views

urlpatterns = [
    path('wishlist',views.wishlist_page,name="wishlist"),
    path('create_wishlist/<id>',views.create_wishlist,name="create_wishlist"),
    path('wishlist_list',views.wishlist_list,name="wishlist_list"),
    path('wishlist_delete/<id>',views.wishlist_delete,name="wishlist_delete"),
    path('wishlist_add/<id>',views.wishlist_add,name="wishlist_add"),
]