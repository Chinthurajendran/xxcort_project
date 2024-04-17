from django.shortcuts import render,redirect
from product.models import products
from user.models import userdata 
from.models import user_wishlist
from cart.models import Cart
from category.models import category
from.models import userdata,products
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# Create your views here.
def wishlist_page(request):
    return render(request, 'user_panal/wishlist.html')

def create_wishlist(request,id):
    if 'email' not in  request.session:
        return redirect('login')
    try:
        current_email = request.session['email']
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('wishlist_list')
    
    try:
        user_data = userdata.objects.get(email = current_email)

        product_data = products.objects.get(id=id)
        list_info = user_wishlist(user_info = user_data,product =product_data)
        messages.success(request, 'Product is add to your wishlist.')
        list_info.save()
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
    except products.DoesNotExist:
        messages.error(request, 'Product not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('wishlist_list')    

def wishlist_list(request):
    if 'email' not in  request.session:
        return redirect('login')
    try:
        current_email = request.session['email']
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('wishlist_list')
    
    blocked_categories = category.objects.filter(is_active = False)
    blocked_product = products.objects.filter(is_active = False)
    out_of_stock_products = products.objects.filter(stock=0)
    
    try:
        user = userdata.objects.get(email = current_email)
        info = user_wishlist.objects.filter(user=user).exclude(
            Q(product_info__product_type__in=blocked_categories) |
            Q(product_info__in=blocked_product) |
            Q(product_info__in=out_of_stock_products)
        )
        # info = user_wishlist.objects.filter(user_info=user)
        context = {'info':info}
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return render(request, 'user_panal/wishlist.html',context)

def wishlist_list(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        current_email = request.session['email']
        user = userdata.objects.get(email=current_email)
        
        blocked_categories = category.objects.filter(is_active=False)
        blocked_products = products.objects.filter(is_active=False)
        out_of_stock_products = products.objects.filter(stock=0)
        
        info = user_wishlist.objects.filter(user_info=user).exclude(
            Q(product__product_type__in=blocked_categories) |
            Q(product__in=blocked_products) |
            Q(product__in=out_of_stock_products)
        )
        
        context = {'info': info}
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('wishlist_list')
    
    return render(request, 'user_panal/wishlist.html', context)


def wishlist_delete(request,id):
    try:
        delete = user_wishlist.objects.get(id=id)
        messages.success(request, 'Product deleted from your wishlist.')
        delete.delete()
    except user_wishlist.DoesNotExist:
        messages.error(request, 'Wishlist item not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('wishlist_list')

def wishlist_add(request,id):
    current_email = request.session.get('email')
    if not current_email:   
        return redirect('login')
    try:
    # user_data = userdata.objects.get(email=current_email)
        user = userdata.objects.get(email = current_email)
        product_id = products.objects.get(id=id)
        product_delete = user_wishlist.objects.get(product=product_id)


    # Attempt to get an existing cart item for the user and product
        size = 'small'
        cart_item = Cart.objects.filter(user=user, product_info=product_id,selected_size=size).first()

    # If cart item doesn't exist, create a new one
        if not cart_item:
            cart_item = Cart.objects.create(user=user, product_info=product_id,selected_size=size)

    # Increment the quantity
        if product_id.stock_for_size(size) < 1:
            messages.error(request,'Not enough stock or quantity limit reached')
            return redirect('cart_view')
        else:
            cart_item.quantity += 0
            cart_item.save()
            product_delete.delete()

        messages.success(request, 'Product added to your cart.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('cart_view')


