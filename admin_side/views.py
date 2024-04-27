from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib import auth
from user.models import userdata
from django.views.decorators.cache import cache_control
from django.http import JsonResponse
from checkout.models import Order_list
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from checkout.models import Order_list
from django.db.models import Q
from coupons.models import Coupons_info,Coupons_User
from django.db.models import Sum
from django.db.models import Count
from wallet.models import Wallet,Transaction
from django.db import transaction
from checkout.models import Checkout_list,Order_list,OrderProduct
from product.models import products
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from category.models import category

# Create your views here.

def index(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        # Retrieve the count of orders with 'Pending' or 'Shipped' status
        order_count = Order_list.objects.filter(Q(order_status='Pending') | Q(order_status='Shipped')).count()
        total_sales = Order_list.objects.filter(order_status='Delivered')
        amount = sum(order.total_amount for order in total_sales)
        total_coupon_usage = Coupons_info.objects.aggregate(total_usage=Sum('usage_count'))['total_usage'] or 0
        total_coupon_codes = Coupons_info.objects.aggregate(total_coupons=Count('coupon_code'))['total_coupons'] or 0
    
    # Create a context dictionary with the order count
        context = {'order_count': order_count,
                'amount':amount,
                'total_coupon_usage':total_coupon_usage,
                'total_coupon_codes':total_coupon_codes}
    # Redirect to 'admin_index' view with the context data
    except Exception as e:
        # Handle other exceptions
        messages.error(request, f'Failed to retrieve data: {str(e)}')
    return render(request, 'admin_panal/admin_index.html',context)

def admin_user_info(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    data = userdata.objects.filter(delete = False)
    return render(request, 'admin_panal/user_info.html',{'data':data})

def admin_user_info_edit(request,id):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        data = userdata.objects.get(id=id)
    except userdata.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('admin_user_info')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        try:
            edit = userdata.objects.get(id=id)
            edit.username = username
            edit.password = password
            edit.email = email
            edit.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_user_info')
        except Exception as e:
            messages.error(request, f'Error occurred during verification: {str(e)}') 
            return render(request, 'admin_panal/user_info_edit.html', {'data': data})
          
    return render(request, 'admin_panal/user_info_edit.html',{'data':data})

def admin_user_info_create(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    if request.method == "POST" :
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        try:
            if userdata.objects.filter(username=username) or userdata.objects.filter(email = email).exists():
                messages.error(request, "Username or email already exists.")
            else:
                data = userdata(username=username,email=email,password=password)
                data.save()
                messages.success(request, 'User created successfully.')
                return redirect('admin_user_info')
        except Exception as e:
            messages.error(request, f'An error occurred during user creation: {str(e)}')
    return render(request, 'admin_panal/user_info_create.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    user = None
    if 'username'in request.session:
        return redirect('admin_index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.username == 'admin':
                auth.login(request, user)
                request.session['username']=username
                return redirect('admin_index')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
                return render(request, 'admin_panal/admin_login.html')
        except Exception as e:
            messages.error(request, f'An error occurred during login: {str(e)}')
    return render(request, 'admin_panal/admin_login.html')

def admin_delete(request,id):
    try:
        obj = userdata.objects.get(id=id)
        obj.delete = True
        obj.save()
        messages.success(request, 'User deleted successfully.')
    except userdata.DoesNotExist:
        messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'An error occurred during user deletion: {str(e)}')
    return redirect('admin_user_info')

def admin_search(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        if 'search' in request.GET:
            search = request.GET['search']
            data = userdata.objects.all()
            if userdata.objects.filter(username__icontains=search, delete=False).exists():
                data = userdata.objects.filter(username__icontains=search, delete=False)
                return render(request, 'admin_panal/user_info.html', {'data': data})
    except Exception as e:
        messages.error(request, f'An error occurred during search: {str(e)}')
    return render(request, 'admin_panal/user_info.html')


def admin_logout(request):
    if 'username' in request.session:
        request.session.flush()
    return redirect('admin_login')

def block_user(request,   user_id):
    try:
        user = get_object_or_404(userdata, id=user_id)

    # Toggle the blocked field
        user.blocked = not user.blocked
        user.save()

        messages.success(request, f'{user.username} has been {"blocked" if user.blocked else "unblocked"}.')

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('admin_user_info')


def new_order_list(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        cancel_orders = Order_list.objects.filter(order_status='processing')
        order_infos = Order_list.objects.order_by('-order_date').exclude(id__in=cancel_orders).all()

                    # Pagination
        paginator = Paginator(order_infos, 6)  # 4 products per page
        page = request.GET.get('page')
        try:
            order_infos = paginator.page(page)
        except PageNotAnInteger:
            order_infos = paginator.page(1)
        except EmptyPage:
            order_infos = paginator.page(paginator.num_pages)

        context = {'order_infos':order_infos}
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'admin_panal/admin_order_details.html',context)


def new_order_approval_list(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        order_approval = Order_list.objects.order_by('-order_date').filter(order_status = 'processing')

                    # Pagination
        paginator = Paginator(order_approval, 6)  # 4 products per page
        page = request.GET.get('page')
        try:
            order_approval = paginator.page(page)
        except PageNotAnInteger:
            order_approval = paginator.page(1)
        except EmptyPage:
            order_approval = paginator.page(paginator.num_pages)

        context = {'order_approval':order_approval}
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'admin_panal/admin_order_approval.html',context)

def order_denied(request,id):
    order = get_object_or_404(Order_list, id=id)
    current_status = order.current_status
    order.order_status = current_status
    order.save()
    messages.success(request, 'Order denial successfully reverted.')
    return redirect('new_order_approval_list')


def admin_order_cancel(request, id):
    try:
        with transaction.atomic():
            # Retrieve order, checkout, and wallet objects
            cancel_order = get_object_or_404(Order_list, id=id)
            current_user = cancel_order.user
            wallet_info = get_object_or_404(Wallet, user=current_user)

            # Check order status and perform appropriate actions
            if cancel_order.current_status == 'Pending':
                # Calculate refund amount
                refund_amount = cancel_order.total_amount

                # Add refund amount to wallet balance
                wallet_info.balance += refund_amount
                wallet_info.save()

                order_products = OrderProduct.objects.filter(order=cancel_order)

                for order_product in order_products:
                    product_name = order_product.product_name
                    product_size = order_product.selected_size
                    product = products.objects.get(name=product_name)  # Assuming your model is named 'Product'
                    quantity_purchased = order_product.quantity
                    
                    # Update the stock of the product for the selected size
                    current_stock = product.stock_for_size(product_size)
                    new_stock = current_stock + quantity_purchased

                    # Update the stock attribute directly based on the size
                    if product_size == 'small':
                        product.small = new_stock
                    elif product_size == 'medium':
                        product.medium = new_stock
                    elif product_size == 'large':
                        product.large = new_stock
                    # Save the changes to the product
                    product.save()
                # Create transaction record for refund
                Transaction.objects.create(
                    wallet=wallet_info,
                    amount=refund_amount,
                    transaction_type='Refund'
                )

                # Delete the order and related checkout info
                cancel_order.order_status = 'Cancelled'
                cancel_order.payment_status = 'Payment Cancelled '
                cancel_order.save()
                # cancel_checkout.delete()

                messages.success(request, 'Order cancelled successfully.')
            elif cancel_order.order_status == 'Shipped':
                messages.error(request, 'Cannot cancel order, product is already shipped.')
            elif cancel_order.order_status == 'Delivered':
                messages.error(request, 'Cannot cancel order, product is already delivered.')
            elif cancel_order.order_status == 'Cancelled':
                messages.error(request, 'Cannot cancel order, product has already been cancelled.')
            else:
                messages.error(request, 'Invalid order status.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('order_list')

def admin_refund(request, id):
    try:
        cancel_order = get_object_or_404(Order_list, id=id)
        current_user = cancel_order.user
        wallet_info = get_object_or_404(Wallet, user=current_user)
    
        order_products = OrderProduct.objects.filter(order=cancel_order)

        for order_product in order_products:
            product_name = order_product.product_name
            product_size = order_product.selected_size
            product = products.objects.get(name=product_name)  # Assuming your model is named 'Product'
            quantity_purchased = order_product.quantity
                    
                    # Update the stock of the product for the selected size
            current_stock = product.stock_for_size(product_size)
            new_stock = current_stock + quantity_purchased

                    # Update the stock attribute directly based on the size
            if product_size == 'small':
                product.small = new_stock
            elif product_size == 'medium':
                product.medium = new_stock
            elif product_size == 'large':
                product.large = new_stock
                    # Save the changes to the product
            product.save()


        with transaction.atomic():
                # Calculate refund amount
            refund_amount = cancel_order.total_amount

                # Add refund amount to wallet balance
            wallet_info.balance += refund_amount
            wallet_info.save()

                # Create transaction record for refund
            Transaction.objects.create(
                wallet=wallet_info,
                amount=refund_amount,
                transaction_type='Refund'
            )

                # Delete the order and related checkout info
            cancel_order.order_status = 'Cancelled'
            cancel_order.payment_status = 'Payment Cancelled '
            cancel_order.save()

            messages.success(request, 'Order refunded successfully.')

    except userdata.DoesNotExist:
        messages.error(request, 'User not found.')
    except (Order_list.DoesNotExist, Checkout_list.DoesNotExist, Wallet.DoesNotExist):
        messages.error(request, 'Order or related data not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('order_list')

def change_status(request,id):
    try:
        if request.method == 'GET':
            new_status = request.GET.get('new_status')
        # Assuming you have a model named Order with a field named status
            orders = Order_list.objects.get(id= id)
            if new_status in ['Pending', 'Shipped', 'Delivered']:  # Assuming these are the valid status options
                orders.order_status = new_status
                orders.save()
            # Adding success message
                messages.success(request, 'Status changed successfully.')
                context = {'new_status':new_status}
    except Order_list.DoesNotExist:
        messages.error(request, 'Order not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    # Redirecting back to the same page or any desired page after status change
    return redirect(reverse('order_list'),context)



def admin_order_in_detail(request, id):
    context = {}  # Initialize context dictionary
    try:
        details = Order_list.objects.get(id=id)
        Order_products = OrderProduct.objects.filter(order=details)

        total_offer = 0  # Initialize total offer
        total = 0

        for product in Order_products:
            category_name = product.category_info
            category_info = category.objects.get(name=category_name)
            if category_info.offer:
                total_offer += category_info.offer 

        for product_price in Order_products:
            product_qty = product_price.quantity
            prices = product_price.price
            total += prices * product_qty

            total_offer_saved = 0  # Initialize total offer saved
            total_product_offer_saved = 0
            
            amount = max(total_offer_saved, total_product_offer_saved)

        context = {
            'details': details, 
            'Order_products': Order_products, 
            'total_offer': total_offer or 0,  # Ensuring default value if total_offer is None
            'total': total
        }
    except Exception as e:
        messages.error(request, f'Failed to retrieve order details: {str(e)}')
    return render(request, 'admin_panal/admin_order_in_detail.html', context)



