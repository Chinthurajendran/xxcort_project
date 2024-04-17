from django.urls import path
from.import views

urlpatterns = [
    path('product_info,<id>',views.product_info,name="product_info"),   
]

