from django.shortcuts import render,redirect
from.models import userdata,products,Cart
from django.http import JsonResponse
from category.models import category
from django.db.models import Q
from user_wishlist.models import user_wishlist
from django.contrib import messages

# Create your views here.
def cart(request):
    return render(request, 'user_panal/cart.html')

def cart_create(request,id):
    if 'email' not in request.session:
        return redirect('user:login')
    
    current_email = request.session['email']
    user = userdata.objects.get(email=current_email)
    product_id = products.objects.get(id=id)
    
    if request.method == 'POST':
        size = request.POST.get('size')
        
        # Check if the size is valid
        valid_sizes = ['small', 'medium', 'large']
        if product_id.stock_for_size(size)<1:
            messages.error(request,'Not enough stock or quantity limit reached')
            return redirect('cart_view')
        if size in valid_sizes:
            # Create or update the cart item
            try:
                # Check if the cart item already exists for the user, product, and size
                cart_item = Cart.objects.get(user=user, product_info=product_id, selected_size=size)
                cart_item.quantity += 0
                cart_item.save()
            except Cart.DoesNotExist:
                # Create a new cart item if it doesn't exist
                cart_item = Cart.objects.create(user=user, product_info=product_id, selected_size=size, quantity=1)
                
            return redirect('cart_view')
        else:
            # Handle invalid size selection, maybe show an error message
            return render(request, 'error_page.html', {'message': 'Invalid size selection'})
    
    # If the request method is not POST or if 'size' is not provided, render the product info page
    return render(request, 'user_panal/product_info.html')



def update_cart_item(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')
        

        cart_item = Cart.objects.get(pk=cart_item_id)
        size = cart_item.product_info.stock_for_size(cart_item.selected_size)

        if action == 'increase':
            max_quantity = 5
            # if cart_item.product_info.stock > cart_item.quantity and cart_item.quantity < max_quantity:
            if cart_item.product_info.stock_for_size(cart_item.selected_size) > cart_item.quantity and cart_item.quantity < max_quantity:
                cart_item.quantity += 1
                cart_item.save()
                val = cart_item.product_info.price * cart_item.quantity
                return JsonResponse({'success': True, 'cart_item_value': val})
            else:
                return JsonResponse({'success': False, 'error': 'Not enough stock or quantity limit reached'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                val = cart_item.product_info.price * cart_item.quantity  
                return JsonResponse({'success': True, 'cart_item_value': val,})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def cart_view(request):
    
    if 'email' not in  request.session:
        return redirect('login')
    try:
        current_email = request.session['email']
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('cart_view')
   
    current_email = request.session['email']
    user = userdata.objects.get(email = current_email)
    blocked_categories = category.objects.filter(is_active = False)
    blocked_product = products.objects.filter(is_active = False)
    stock_products_small = products.objects.filter(small=0)
    stock_products_medium = products.objects.filter(medium=0)
    stock_products_large = products.objects.filter(large=0)

    cart_items = Cart.objects.filter(user=user).exclude(
        Q(product_info__product_type__in=blocked_categories) |
        Q(product_info__in=blocked_product) |
        Q(product_info__in=stock_products_small)|
        Q(product_info__in=stock_products_medium)|
        Q(product_info__in=stock_products_large)
    )


    total_subtotal = sum(cart_item.product_info.price * cart_item.quantity for cart_item in cart_items)
    context = {'cart_items':cart_items,'total_subtotal': total_subtotal}
    return render(request,'user_panal/cart.html',context)

def cart_delete(request,id):
    delete_items = Cart.objects.get(id=id)
    delete_items.delete()
    return redirect('cart_view')


