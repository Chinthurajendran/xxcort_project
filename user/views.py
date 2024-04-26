from django.shortcuts import render,redirect
from django.views.decorators.cache import cache_control
from.models import userdata,Address1,Address2
from django.core.mail import send_mail
from django.contrib import messages
import random
from django.contrib.auth import logout
from django.db.models import Q
from django.conf import Settings
from checkout.models import Checkout_list,Order_list,OrderProduct
from django.contrib import auth
from category.models import category
from product.models import products
from wallet.models import Wallet,Transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404
import re
from checkout.models import OrderProduct
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from decouple import config

# Create your views here.

def index(request):

    # Check if user is authenticated
    blocked_categories = category.objects.filter(is_active=False)
    blocked_product = products.objects.filter(is_active=False)
    collections = products.objects.exclude(product_type__in=blocked_categories).exclude(id__in=blocked_product).order_by('name')
    data = category.objects.all()

    # Aggregate the order products to get the count of each product
    order_products_counts = OrderProduct.objects.values('product_name').annotate(total_purchases=Count('product_name')).order_by('-total_purchases')[:11]
    # Extract the product names
    max_products = [item['product_name'] for item in order_products_counts]
    # Retrieve the products that match the top 10 best-selling product names
    best_collections = products.objects.exclude(product_type__in=blocked_categories) \
                                         .exclude(id__in=blocked_product) \
                                         .filter(name__in=max_products) \
                                         .order_by('id')[:11]
    
    order_products_counts = OrderProduct.objects.values('category_info').annotate(total_purchases=Count('category_info')).order_by('-total_purchases')[:10]
    # Extract the product names
    max_products = [item['category_info'] for item in order_products_counts]
    # Retrieve the products that match the top 10 best-selling product names
    best_category = products.objects.exclude(product_type__in=blocked_categories) \
                                         .exclude(id__in=blocked_product) \
                                         .filter(product_type__name__in=max_products) \
                                         .order_by('id')[:10]

    context = {'collections': collections, 'data': data, 'best_collections': best_collections,'best_category': best_category}
    return render(request, 'user_panal/index.html', context)

def search(request):
    try:
        if 'search' in request.GET:
            search = request.GET['search']
            collections = products.objects.all()
            if products.objects.filter(name__icontains=search).exists():
                collections = products.objects.filter(name__icontains=search)
                return render(request, 'user_panal/index.html', {'collections': collections})
    except Exception as e:
        messages.error(request, f'An error occurred during search: {str(e)}')
    return render(request, 'user_panal/index.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if 'email' in request.session:
        return redirect('index')
                    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = userdata.objects.get(email = email,delete = False)
            if user.blocked:
                messages.error(request, 'Your account is blocked.')
            else:
                if password == user.password:
                    request.session['email'] = email
                    messages.success(request, 'User logged in successfully.')
                    return redirect('index')
                else:
                    messages.error(request, 'Invalid username or password. Please try again.')
        except ObjectDoesNotExist:
            messages.error(request, 'No account found with this email.')

    return render(request, 'user_panal/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        email = request.POST.get('email')
        
        
        # Check if a user with the same username or email exists
        try:
            existing_user = userdata.objects.filter(Q(username=username) | Q(email=email), delete=True)
        
            if existing_user.filter(delete=False).exists():
                messages.error(request, 'Username or email already exists.')
            else:
                if password == re_password:
                    if not validate_password(password):
                        messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
                        return redirect('signup')
                    request.session['email'] = email
                    request.session['password'] = password
                    request.session['username'] = username
                    return redirect('send_otp')
                else:
                    messages.error(request, 'Passwords do not match.')
        except ObjectDoesNotExist:
            messages.error(request, 'Error occurred during signup. Please try again.')
        except Exception as e:
                messages.error(request, f'Error occurred during signup: {str(e)}')

    return render(request, 'user_panal/signup.html')


def validate_password(password):
    # Check if password is at least 6 characters long, includes one number, and has no spaces
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', password))


def google_oauth_callback(request):
    return redirect('index')


def send_otp(request):
    if 'email' in request.session:
        email = request.session['email']
        random_num = random.randint(1000, 9999)
        request.session['OTP_Key'] = random_num
        print(random_num)
        try:
            send_mail(
                "OTP AUTHENTICATING XXCORT",
                f"{random_num} -OTP",
                "chinthurajendran143@gmail.com",  # Your Gmail address
                [email],
                auth_user=config('EMAIL_HOST_USER'),  # Your Gmail address
                auth_password=config('EMAIL_HOST_PASSWORD'),  # Your App Password
                fail_silently=False,
            )
            return redirect('verification')
        except Exception as e:
            messages.error(request, f"Error sending email: {e}")
    else:
        messages.error(request, 'Email not found in session.')
    return render(request, 'user_panal/send_otp.html')

def verification(request):
    if request.method == 'POST':
        print('chinthu')
        try:
            if str(request.session['OTP_Key']) != str(request.POST['otp']):
                messages.error(request, "Invalid OTP. Please try again.")
                print(request.session['OTP_Key'], request.POST['otp'])
            else:
                log_obj = userdata(username=request.session['username'],
                                    password=request.session['password'], 
                                    email=request.session['email'])
                log_obj.save()
                messages.success(request, 'User registered successfully.')
                return redirect('login')
            messages.error(request, 'Invalid OTP. Please try again.')
        except Exception as e:
            messages.error(request, f'Error occurred during verification: {str(e)}')
    return render(request, 'user_panal/send_otp.html')

def resend_otp(request):
    if 'OTP_Key' in request.session:
        del request.session['OTP_Key']
        
        try:
            random_num = random.randint(1000,9999)
            request.session['OTP_Key'] = random_num
            send_mail(
            
                    'OTP AUTHENTICATING XXCORT',
                    f"{random_num} -OTP",
                    'chinthurajendran143@gmail.com',
                    [request.session.get('email')],
                    fail_silently =False,
            )
            messages.success(request, 'OTP Resend successfully.')
        except Exception as e:
                messages.error(request, f'Error occurred during OTP sending: {str(e)}')
    else:
        messages.error(request, 'Email not found in session.')
    return redirect('verification') 



def logout(request):
    if 'email' in request.session:
        try:
            request.session.flush()
            messages.success(request, 'User logout successfully.')
        except Exception as e:
            messages.error(request, f'An error occurred during logout: {str(e)}')
    return redirect('index')

def forgot_password(request):
    if request.method =='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')

        try:
            user_exists = userdata.objects.filter(email=email).exists()
            if user_exists and password == re_password:
                if not validate_password(password):
                        messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
                        return redirect('forgot_password')
                user_instance = userdata.objects.get(email=email)
                user_instance.password = password
                user_instance.save()
                messages.success(request, 'Password successfully changed.')
                return redirect('login')
            else:
                messages.error(request, 'Incorrect password or user does not exist. Please try again.') 
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'user_panal/forgot_password.html')


def new_collection(request):
    return render(request, 'user_panal/new_collection.html')

def product_info(request):
    return render(request, 'user_panal/product_info.html')


def user_index(request):
    return render(request,'user_panal/user_index.html')

def user_profile(request):
    if 'email' not in  request.session:
        return redirect('login')
    try:
        current_email = request.session['email']
        user_data = userdata.objects.get(email = current_email,delete = False)
        context = {
        'user_data': user_data
        }
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')

    return render(request, 'user_panal/user_profile.html', context)

def user_profile_edits(request):
    current_email = request.session.get('email')
    try:
        data = userdata.objects.get(email=current_email)
        context = {'data': data}
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('user_profile')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        try:
            edit = userdata.objects.get(email = current_email)
            edit.username = username
            edit.email = email
            edit.save()
            messages.success(request, 'Successfully updated.')
            return redirect('user_profile')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    return render(request,'user_panal/user_profile_edits.html',context)


def user_profile_address_create(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        current_email = request.session['email']
        user = userdata.objects.get(email=current_email)
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('user_profile')


    if request.method == 'POST':
        address = request.POST['address']
        locality = request.POST['locality']
        pincode = request.POST['pincode']
        district = request.POST['district']
        state = request.POST['state']

        try:
        # Check if the address already exists
            existing_address = Address1.objects.filter(
                user=user
            )
    

            if existing_address.exists():
                messages.error(request, 'Address already exists.')
                return render(request, 'user_panal/user_profile_address.html')
           
            else:
            # Create a new Address1 instance and save it
                new_address = Address1(
                    address=address,
                    locality=locality,
                    pincode=pincode,
                    district=district,
                    state=state,
                    user=user
                )
                messages.success(request, 'Your address has been created successfully')
                new_address.save()

            return redirect('user_profile_address')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'user_panal/user_profile_address_create.html')

def user_profile_address(request):
    if 'email' not in request.session:
        return redirect('login')
    try:
        email = request.session['email']
        user = userdata.objects.get(email=email)
        user_addresses = Address1.objects.filter(user=user)
        context = {'user_addresses': user_addresses}
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('user_profile')
    except Address1.DoesNotExist:
        messages.info(request, 'No addresses found for the user.')
        return redirect('user_profile')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return render(request, 'user_panal/user_profile_address.html', context)


def user_profile_address_edit(request,id):
    try:
        data = Address1.objects.get(id=id)
        context = {'data':data}
    except Address1.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('user_profile_address') 

    if request.method == "POST":
        address = request.POST.get('address')
        locality = request.POST.get('locality')
        pincode = request.POST.get('pincode')
        district = request.POST.get('district')
        state = request.POST.get('state')
        try:
            edit = Address1.objects.get(id=id)
            edit.address = address
            edit.locality =locality
            edit.pincode = pincode
            edit.state = state
            edit.district = district
            edit.save()
            messages.success(request, 'Successfully updated.')
            return redirect('user_profile_address')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
    return render(request,'user_panal/user_profile_address_edit.html',context)

def user_profile_address_delete(request,id):
    try:
        data = Address1.objects.get(id=id)
        data.delete()
        messages.success(request, 'Billing address deleted successfully.')
    except Address1.DoesNotExist:
        messages.error(request, 'Address not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('user_profile_address_create')

def sec_user_profile_address(request):
    if 'email' not in request.session:
        return redirect('login')
    try:
        email = request.session['email']
        user = userdata.objects.get(email=email)
        user_addresses = Address2.objects.filter(user=user)
        context = {'user_addresses': user_addresses}
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')
    return render(request,'user_panal/sec_user_profile_address.html',context)

def sec_user_profile_address_edit(request,id):

    try:
        data = Address2.objects.get(id=id)
        context = {'data':data}
    except Address2.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('sec_user_profile_address')

    if request.method == "POST":
        address = request.POST.get('address')
        locality = request.POST.get('locality')
        pincode = request.POST.get('pincode')
        district = request.POST.get('district')
        state = request.POST.get('state')

        try:
            edit = Address2.objects.get(id=id)
            edit.address = address
            edit.locality =locality
            edit.pincode = pincode
            edit.state = state
            edit.district = district
            edit.save()
            messages.success(request, 'Successfully updated.')
            return redirect('sec_user_profile_address')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request,'user_panal/sec_user_profile_address_edit.html',context)

def sec_user_profile_address_create(request):
    if 'email' not in request.session:
        return redirect('login')
    
    try:
        current_email = request.session['email']
        user = userdata.objects.get(email=current_email)
    except userdata.DoesNotExist:
        messages.error(request, 'User data not found.')
        return redirect('sec_user_profile_address')

    if request.method == 'POST':
        address = request.POST['address']
        locality = request.POST['locality']
        pincode = request.POST['pincode']
        district = request.POST['district']
        state = request.POST['state']

        # Check if the address already exists
        existing_address = Address2.objects.filter(user=user)
        if existing_address.exists():
            messages.success(request, 'Address already exists.')
        else:
            try:
                # Create a new Address2 instance and save it
                new_address = Address2(
                    address=address,
                    locality=locality,
                    pincode=pincode,
                    district=district,
                    state=state,
                    user=user
                )
                new_address.save()
                messages.success(request, 'Your address has been created successfully')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('sec_user_profile_address')

        return redirect('sec_user_profile_address')
    return render(request, 'user_panal/sec_user_profile_address_create.html')

def sec_user_profile_address_delete(request,id):
    data = Address2.objects.get(id=id)
    data.delete()
    messages.success(request, 'Shipping address deleted successfully.')
    return redirect('sec_user_profile_address_create')


def user_profile_change_password_edit(request):
    try:
        current_email = request.session['email']
    except KeyError:
        messages.error(request, 'Email not found in session.')
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirom_password = request.POST.get('confirom_password')
        
        if password == confirom_password:
            if not validate_password(password):
                    messages.error(request, 'Password must be at least 6 characters long, including one number, and no spaces.')
                    return redirect('user_profile_change_password_edit')
            try:
                edit = userdata.objects.get(email= current_email)
                edit.password = password
                edit.save()
                logout(request)
                messages.success(request, 'Password changed successfully. Please log in again.')
                return redirect("login")
            except userdata.DoesNotExist:
                messages.error(request, 'User data not found.')
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        else:
             messages.error(request, 'Password does not match.')
    return render(request, 'user_panal/user_profile_change_password_edit.html')

def order_details(request):
    try:
        current_email = request.session['email']
        user = userdata.objects.get(email = current_email)
        order_info = Order_list.objects.filter(user=user).order_by('-order_date')

                            # Pagination
        paginator = Paginator(order_info, 6)  # 4 products per page
        page = request.GET.get('page')
        try:
            order_info = paginator.page(page)
        except PageNotAnInteger:
            order_info = paginator.page(1)
        except EmptyPage:
            order_info = paginator.page(paginator.num_pages)

        context = {'order_info':order_info}
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')     

    return render(request, 'user_panal/order_details.html',context)

def order_cancel(request, id):
    current_email = request.session.get('email')
    user = userdata.objects.get(email = current_email)
    try:
        with transaction.atomic():
            # Retrieve order, checkout, and wallet objects
            cancel_order = get_object_or_404(Order_list, id=id)
            wallet_info = get_object_or_404(Wallet, user=user)

            # Check order status and perform appropriate actions
            if cancel_order.order_status == 'Pending':
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

    return redirect('order_details')


def refund(request, id):
    try:
        current_email = request.session.get('email')
        user = userdata.objects.get(email=current_email)
        cancel_order = get_object_or_404(Order_list, id=id, user=user)
        wallet_info = get_object_or_404(Wallet, user=user)
    
        if cancel_order.order_status == 'Delivered':

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
        else:
            messages.error(request, 'Cannot refund order. The order must be delivered.')

    except userdata.DoesNotExist:
        messages.error(request, 'User not found.')
    except (Order_list.DoesNotExist, Checkout_list.DoesNotExist, Wallet.DoesNotExist):
        messages.error(request, 'Order or related data not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('order_details')


@require_POST
def submit_cancellation_reason(request, id):
    # Extract cancellation reason and order ID from POST data
    current_email = request.session.get('email')
    user = userdata.objects.get(email=current_email)
    
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        
        # Extract the reason for cancellation
        reason = data.get('reason', '')

        # Check if the order exists
        admin_approval = get_object_or_404(Order_list, id=id, user=user)
        status = admin_approval.order_status

        # Update order status and save cancellation reason to the database
        admin_approval.reason = reason
        admin_approval.current_status =status
        admin_approval.order_status = 'processing'
        admin_approval.save()

        # Respond with success message
        messages.success(request, 'Cancellation reason submitted successfully')
        return JsonResponse({'success': True})

    except userdata.DoesNotExist:
        # Return a failure response if the user does not exist
        return JsonResponse({'success': False, 'error': 'User does not exist'}, status=404)

    except Order_list.DoesNotExist:
        # Return a failure response if the order does not exist
        return JsonResponse({'success': False, 'error': 'Order does not exist'}, status=404)
    
    except Exception as e:
        # Return a failure response for other exceptions
        return JsonResponse({'success': False, 'error': str(e)}, status=500)




