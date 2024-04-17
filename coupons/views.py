from django.shortcuts import render,redirect
from.models import Coupons_info,Coupons_User,Reference_coupon
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from checkout.models import Checkout_list,Order_list,OrderProduct
from cart.models import Cart
from user.models import userdata,Address1,Address2
from decimal import Decimal
import razorpay
from django.views.decorators.csrf import csrf_exempt
from wallet.models import Transaction,Wallet
from .models import Coupons_info,Coupons_User
from django.db.models import Q
from .code import generate_coupon_code
from django.http import JsonResponse

# Create your views here.
def coupons_info(request):
    coupons_data = Coupons_info.objects.all()
    context = {'coupons_data':coupons_data,}
    return render(request,'admin_panal/coupon.html',context)

def coupons_create(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        if request.method == 'POST':
            code = request.POST['coupon_code']
            offer = request.POST['coupon_offer']
        
            # Check if coupon with the same code already exists
            if Coupons_info.objects.filter(coupon_code=code).exists():
                messages.error(request, 'Coupon with the same code already exists.')
            else:
                # If not, create and save the coupon
                data = Coupons_info(coupon_code=code, discount_percentage=offer)
                data.save()
                messages.success(request, 'Coupon created successfully.')
                return redirect('coupons_info')

    except KeyError:
        messages.error(request, 'Invalid data provided.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return render(request, 'admin_panal/coupons_create.html')

def coupons_delete(request,id):
    try:
        coupon_remove = Coupons_info.objects.get(id=id)
        coupon_remove.delete()
        messages.success(request, 'Coupon deleted successfully.')
    except Coupons_info.DoesNotExist:
        messages.error(request, 'Coupon does not exist.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('coupons_info')

def coupons_edit(request,id): 
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        coupon_details = Coupons_info.objects.get(id=id)
        if request.method == 'POST':
            code = request.POST['coupon_code']
            offer = request.POST['coupon_offer']
            if int(offer) < 1:
                messages.error(request, 'Offer amount must be greater than or equal to 1.')
                return redirect('coupons_edit', id=id)
            edit = Coupons_info.objects.get(id=id)
            edit.coupon_code = code
            edit.discount_percentage =offer
            edit.save()
            messages.success(request, 'Coupon updated successfully.')
            return redirect('coupons_info')
        context = {'coupon_details':coupon_details}
    except Coupons_info.DoesNotExist:
        messages.error(request, 'Coupon does not exist.')
        return redirect('coupons_info') 
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('coupons_info')
    return render(request,'admin_panal/coupons_edit.html',context)

def coupons_block(request,coupon_id):
    try:
        user = get_object_or_404(Coupons_info, id=coupon_id)

        user.is_active = not user.is_active
        user.save()

        messages.success(request, f'{user.coupon_code} has been {"blocked" if user.is_active else "unblocked"}.')
    except Coupons_info.DoesNotExist:
        messages.error(request, 'Coupon not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('coupons_info')

def checkout_coupon(request):
    email = request.session.get('email')
    try:
        user = userdata.objects.get(email=email)
    except userdata.DoesNotExist:
        messages.error(request, "User does not exist. Please log in again.")
        return redirect('login')  # Redirect to login page if user does not exist

    cart_info = Cart.objects.filter(user=user)
    
    # Check if the cart is empty
    if not cart_info.exists():
        messages.error(request, "Your cart is empty. Please add products before checking out.")
        return redirect('cart_view')
    
    add1 = Address1.objects.filter(user=user)
    add2 = Address2.objects.filter(user=user)

    # Calculate the subtotal for each item in the cart_info queryset
    sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
    shipping = 100
    
    # Retrieve the stored coupon code from the session
    coupon_code = request.session.get('coupon_code')

    # Initialize offer to 0
    offer = 0

    # Retrieve the coupon object based on the stored coupon code
    if coupon_code:
        try:
            coupon = Coupons_info.objects.get(coupon_code=coupon_code)
            offer = coupon.discount_percentage  # Access the discount_percentage attribute
        except Coupons_info.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
            return redirect('cart_view')
        
    Total = sub_total + shipping - offer  # Apply discount percentage
    
    context = {
        'cart_info': cart_info,
        'sub_total': sub_total,
        'add1': add1,
        'add2': add2,
        'shipping': shipping,
        'Total': Total,
        'offer': offer
    }
    
    return render(request, 'user_panal/checkout_coupon.html', context)

def coupon_create_order(request):
    try:
        email = request.session.get('email')
        user_data = userdata.objects.get(email=email)
    
        cart_info = Cart.objects.filter(user=user_data)
        coupon_code = request.session.get('coupon_code')

        # Initialize offer to 0
        offer = 0

        # Retrieve the coupon object based on the stored coupon code
        if coupon_code:
            try:
                coupon = Coupons_info.objects.get(coupon_code=coupon_code)
                offer = coupon.discount_percentage
            except Coupons_info.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
                return redirect('check_out')
        
        sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping = 100
        total_amount = sub_total + shipping - offer

        request.session['subtotal'] = str(sub_total)
        request.session['total_amount'] = str(total_amount)
    
        if request.method == 'POST':
            checkbox_value = request.POST.get('checkbox')

            if checkbox_value in ['Billing', 'shipping_info']:  # Ensure that at least one checkbox is selected
                if checkbox_value == 'Billing':
                    address = request.POST.get('billing_address')
                    locality = request.POST.get('city')
                    pincode = request.POST.get('zipcode')
                    district = request.POST.get('state')
                    state = request.POST.get('state')
                elif checkbox_value == 'shipping_info':
                    address = request.POST.get('shipping_address')
                    locality = request.POST.get('shipping_city')
                    pincode = request.POST.get('shipping_pincode')
                    district = request.POST.get('shipping_district')
                    state = request.POST.get('shipping_state')

                request.session['billing_address'] = address
                request.session['billing_locality'] = locality
                request.session['billing_pincode'] = pincode
                request.session['billing_district'] = district
                request.session['billing_state'] = state
            
                return redirect('payment_method_coupon')
            else:
                messages.error(request,"Please select either 'Billing' or 'Shipping' option.")
                return redirect('checkout_coupon')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    
    return redirect('check_out')



def add_coupon(request):
    # Retrieve the current user's email from session
    current_email = request.session.get('email')

    # Retrieve the user object based on the email
    try:
        user = userdata.objects.get(email=current_email)
    except userdata.DoesNotExist:
        # Handle the case where user does not exist
        messages.error(request, "User does not exist.")
        return redirect('checkout_coupon')

    if request.method == 'POST':
        try:
            # Retrieve the coupon code from the form
            code = request.POST.get('coupon')

            # Retrieve the coupon object based on the provided code
            try:
                coupon = Coupons_info.objects.get(coupon_code=code)
            except Coupons_info.DoesNotExist:
                messages.error(request, "Invalid coupon code.")
                return redirect('check_out')

            # Checking if the coupon exists in Coupons_User table
            if coupon.usage_count==1:
                messages.error(request, "You have already used this coupon.")
                return redirect('check_out')

            # Retrieve the cart items for the current user
            cart_info = Cart.objects.filter(user=user)

            total_offer_saved = 0  # Initialize total offer saved
            total_product_offer_saved = 0

            for cart_item in cart_info:
                if cart_item.product_info.product_type.offer is not None:
                    total_offer_saved += cart_item.product_info.product_type.offer
            
            for cart_item in cart_info:
                price = cart_item.product_info.price
                offer_price = cart_item.product_info.offer_price
                amount_saved = price - offer_price
                total_product_offer_saved += amount_saved

            # Determine the maximum offer saved
            amount = max(total_offer_saved, total_product_offer_saved)

            # Calculate the total offer saved from product types in the cart
            # total_offer_saved = sum(cart_item.product_info.product_type.offer or 0 for cart_item in cart_info)

            if coupon.discount_percentage < amount:
                messages.error(request, "The discount provided by the coupon is lower than the total offer saved.")
                return redirect('check_out')

            # If the coupon exists and hasn't been used by the user, associate it with the user
            # Coupons_User.objects.create(user=user, coupon=coupon)
            request.session['coupon_code'] = code
            messages.success(request, "Coupon added successfully.")
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    # Redirect to the checkout_coupon page
    return redirect('checkout_coupon')

def payment_method_coupon(request):
    return render(request,'user_panal/payment_method_coupon.html')

def coupon_cod(request):
    try:
        email = request.session.get('email')
        user_data = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user=user_data)

        # Fetching subtotal and coupon code from session
        sub_total = request.session.get('subtotal')
        coupon_code = request.session.get('coupon_code')

        if coupon_code:
            coupon = Coupons_info.objects.get(coupon_code=coupon_code)
            coupon.usage_count += 1
            coupon.save()
            offer = coupon.discount_percentage
            coupon_info=Coupons_User.objects.create(coupon=coupon,user = user_data)
            coupon_info.save()

        # Fetching billing address details from session
        address = request.session.get('billing_address')
        total_amount = request.session.get('total_amount')
        locality = request.session.get('billing_locality')
        pincode = request.session.get('billing_pincode')
        district = request.session.get('billing_district')
        state = request.session.get('billing_state')

        # Creating an Order_list entry with coupon discount
        order_instance = Order_list.objects.create(
            user=user_data,
            total_amount=total_amount,
            billing_address=address,
            billing_locality=locality,
            billing_pincode=pincode,
            billing_district=district,
            billing_state=state,
            coupon=coupon.discount_percentage if coupon else 0
        )

        # Creating OrderProduct entries for each cart item
        for cart_item in cart_info:
            OrderProduct.objects.create(
                user=user_data,
                order=order_instance,
                product_name=cart_item.product_info.name,
                code=cart_item.product_info.code,
                category_info=cart_item.product_info.product_type.name,
                quantity=cart_item.quantity,
                selected_size = cart_item.selected_size,
                price=cart_item.product_info.price,
                offer=cart_item.product_info.offer
            )

            product = cart_item.product_info
            selected_size = cart_item.selected_size
            quantity_purchased = cart_item.quantity
            current_stock = product.stock_for_size(selected_size)
            
            # Subtract the quantity purchased from the current stock
            new_stock = current_stock - quantity_purchased
            
            # Update the stock for the selected size
            if selected_size == 'small':
                product.small = new_stock
            elif selected_size == 'medium':
                product.medium = new_stock
            elif selected_size == 'large':
                product.large = new_stock
            
            # Save the changes to the product
            product.save()

        # Clearing cart after successful order
        cart_info.delete()

    except Exception as e:
        # Handling exceptions and displaying error messages
        messages.error(request, f'An error occurred: {str(e)}')

    # Redirecting to checkout success page
    return redirect('check_out_success')

def razorpay_payment_coupon(request):
    email = request.session.get('email')
    if email is None:
        return redirect('check_out')  # Redirect to checkout page if email is not in session
    
    try:
        user = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user=user)
        coupon_code = request.session.get('coupon_code')

        # Retrieve coupon information and validate
        offer = 0
        if Coupons_info.objects.filter(coupon_code=coupon_code).exists():
            coupon = Coupons_info.objects.get(coupon_code=coupon_code)
            offer = coupon.discount_percentage
        else:
            # Handle the case where the coupon code is not found or invalid
            messages.error(request, "Coupon not found or invalid.")
            return redirect('checkout_coupon')

        # Calculate total amount with coupon discount
        sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping = 100
        total_amount = sub_total + shipping - offer

        # Initialize Razorpay payment
        amount = total_amount  # Example amount in paise, change as per your requirement
        currency = "INR"

        client = razorpay.Client(auth=("rzp_test_tFO7oGhYPMf1B2", "CHcnMspVfaQAHR4UuhsMXoyP"))
        payment = client.order.create({
            "amount": int(amount * 100),  # Convert to paise
            "currency": currency,
            "payment_capture": '1'  # Auto capture payment
        })

        context = {
            "payment_details": {
                "id": payment['id'],  # Use the generated order ID
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "key": "rzp_test_tFO7oGhYPMf1B2", 
                "email": email, 
            }
        }
        return render(request, "user_panal/razorpay_coupon.html", context)
    except userdata.DoesNotExist:
        messages.error(request, 'Customer not found.')
    except Exception as e:
        messages.error(request, f'Razorpay payment failed: {str(e)}')
    
    return redirect('checkout_coupon')

 


@csrf_exempt
def coupon_payment_success(request):
    return render(request,'user_panal/coupon_payment_success.html')


def coupon_razorpay_payment(request):
    try:
        email = request.session.get('email')
        user = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user=user)
        coupon_code = request.session.get('coupon_code')

        if coupon_code:
            coupon = Coupons_info.objects.get(coupon_code=coupon_code)
            coupon.usage_count += 1
            coupon.save()
            offer = coupon.discount_percentage
            coupon_info=Coupons_User.objects.create(coupon=coupon,user = user)
            coupon_info.save()

        # Retrieve billing address details from session
        address = request.session['billing_address']
        total_amount = request.session['total_amount']
        locality = request.session['billing_locality']
        pincode = request.session['billing_pincode']
        district = request.session['billing_district']
        state = request.session['billing_state']

        # Create Order_list entry with coupon discount
        order_instance = Order_list.objects.create(
            user=user,
            total_amount=total_amount,
            billing_address=address,
            billing_locality=locality,
            billing_pincode=pincode,
            billing_district=district,
            billing_state=state,
            coupon=coupon.discount_percentage if coupon else 0,
            payment_status="Amount is paid", 
            payment_method="Online banking"
        )

        # Create OrderProduct entries for each cart item
        for cart_item in cart_info:
            OrderProduct.objects.create(
                user=user,
                order=order_instance,
                product_name=cart_item.product_info.name,
                code=cart_item.product_info.code,
                category_info=cart_item.product_info.product_type.name,
                quantity=cart_item.quantity,
                selected_size = cart_item.selected_size,
                price=cart_item.product_info.price,
                offer=cart_item.product_info.offer
            )

            # Deduct purchased quantities from product stock
            product = cart_item.product_info
            product.stock -= cart_item.quantity
            product.save()

                    # for cart_item in cart_info:
            product = cart_item.product_info
            selected_size = cart_item.selected_size
            quantity_purchased = cart_item.quantity
            current_stock = product.stock_for_size(selected_size)
            
            # Subtract the quantity purchased from the current stock
            new_stock = current_stock - quantity_purchased
            
            # Update the stock for the selected size
            if selected_size == 'small':
                product.small = new_stock
            elif selected_size == 'medium':
                product.medium = new_stock
            elif selected_size == 'large':
                product.large = new_stock
            
            # Save the changes to the product
            product.save()

        # Clear cart after successful order
        cart_info.delete()

    except Exception as e:
        messages.error(request, f'Razorpay payment failed: {str(e)}')

    return redirect('order_details')

def coupan_wallet_payment_success(request):
    return render(request,'user_panal/coupan_wallet_payment_success.html')


from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404

def coupan_razorpay_wallet_payment_success(request):
    try:
        email = request.session.get('email')
        if email is None:
            return redirect('check_out')
        
        user = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user=user)
        coupon_code =request.session.get('coupon_code')
        offer = 0
        
        if coupon_code:
            coupon = Coupons_info.objects.get(coupon_code=coupon_code)
            coupon.usage_count += 1
            coupon.save()
            offer = coupon.discount_percentage
            coupon_info=Coupons_User.objects.create(coupon=coupon,user = user)
            coupon_info.save()
        
        sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping = 100
        amount = sub_total + shipping - offer
        
        wallet_info = Wallet.objects.get(user=user)
        wallet_info.balance -= amount
        wallet_info.save()

        transation_info = Transaction.objects.create(
            wallet=wallet_info,
            amount=amount,
            transaction_type='Debit'
        )
        transation_info.save()

        address = request.session.get('billing_address')
        total_amount = request.session.get('total_amount')
        locality = request.session.get('billing_locality')
        pincode = request.session.get('billing_pincode')
        district = request.session.get('billing_district')
        state = request.session.get('billing_state')

        order_instance = Order_list.objects.create(
            user=user,
            total_amount=total_amount,
            billing_address=address,
            billing_locality=locality,
            billing_pincode=pincode,
            billing_district=district,
            billing_state=state,
            coupon=coupon.discount_percentage if coupon else 0,
            payment_status="Amount is paid",
            payment_method="Online banking"
        )

        for cart_item in cart_info:
            OrderProduct.objects.create(
                user=user,
                order=order_instance,
                product_name=cart_item.product_info.name,
                code=cart_item.product_info.code,
                category_info=cart_item.product_info.product_type.name,
                quantity=cart_item.quantity,
                selected_size = cart_item.selected_size,
                price=cart_item.product_info.price,
                offer=cart_item.product_info.offer
            )

            product = cart_item.product_info
            selected_size = cart_item.selected_size
            quantity_purchased = cart_item.quantity
            current_stock = product.stock_for_size(selected_size)
            
            # Subtract the quantity purchased from the current stock
            new_stock = current_stock - quantity_purchased
            
            # Update the stock for the selected size
            if selected_size == 'small':
                product.small = new_stock
            elif selected_size == 'medium':
                product.medium = new_stock
            elif selected_size == 'large':
                product.large = new_stock
            
            # Save the changes to the product
            product.save()

        cart_info.delete()
        
    except Exception as e:
        messages.error(request, f'Razorpay payment failed: {str(e)}') 

    return redirect('order_details')

def generate_coupon(request):
    email = request.session.get('email')
    user = userdata.objects.get(email=email)
    coupon_code = generate_coupon_code()
    code = Reference_coupon(reference_coupon_code = coupon_code,user = user)
    code.save()
    return JsonResponse({'coupon_code': coupon_code})

def Reference_code(request):
    coupons_data = Reference_coupon.objects.all()
    context = {'coupons_data':coupons_data,}
    return render(request,'admin_panal/Reference_code.html',context)


def wallet_point(request):
    current_email = request.session.get('email')
    try:
        user = userdata.objects.get(email=current_email)
        
        if request.method == 'POST':
            code = request.POST.get('code')
            try:
                reference = Reference_coupon.objects.get(reference_coupon_code=code)
                
                # Check if the reference code is generated by the user themselves
                if reference.user == user:
                    messages.error(request, "You cannot use a reference code generated by yourself.")
                else:
                    wallet_info = Wallet.objects.get(user=user)
                    amount_info = reference.discount_percentage
                    wallet_info.balance += amount_info

                    # Create transaction for the user who used the reference code
                    transaction_info = Transaction.objects.create(
                        wallet=wallet_info,
                        amount=amount_info, 
                        transaction_type='Point')
                    messages.success(request,"Points added successfully.")
                    transaction_info.save()

                    # Add points to the user who generated the reference code
                    gen_user = reference.user

                    # Check if the user has a wallet
                    try:
                        wallet_generator = Wallet.objects.get(user=gen_user)
                    except Wallet.DoesNotExist:
                        # If the wallet doesn't exist, create a new wallet for the user
                        wallet_generator = Wallet.objects.create(user=gen_user, balance=0)

                    # Now you can update the balance
                    wallet_generator.balance += amount_info
                    wallet_generator.save()


                    # Create transaction for the user who generated the reference code
                    transaction_generator = Transaction.objects.create(
                        wallet=wallet_generator,
                        amount=amount_info,
                        transaction_type='Point'
                    )
                    transaction_generator.save()
            except Reference_coupon.DoesNotExist:
                messages.error(request, "Invalid reference code.")
    
    except userdata.DoesNotExist:
        messages.error(request, "User data not found.")
    
    return redirect('wallet')


    
