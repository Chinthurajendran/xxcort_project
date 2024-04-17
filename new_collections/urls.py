from django.urls import path
from.import views

urlpatterns = [
    # path('new_collection',views.new_collection,name="new_collection"),
    # path('index',views.index,name="index"),
    # path('new_collection1',views.new_collection1,name="new_collection1"),
    # path('new_collection_ase_price',views.new_collection_ase_price,name="new_collection_ase_price"),
    # path('new_collection_des_price',views.new_collection_des_price,name="new_collection_des_price"),
    # path('new_collection_index',views.new_collection_index,name="new_collection_index"),

    path('new_collection/', views.new_collection, name='new_collection'),

]
   


