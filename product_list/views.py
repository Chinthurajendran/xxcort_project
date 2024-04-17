from django.shortcuts import render
from product.models import products

# Create your views here.

def product_info(request,id):
    product_data = products.objects.get(id=id)
    context = {'product_data':product_data}
    return render(request,"user_panal/product_info.html",context)

    
