from django.shortcuts import render, redirect,HttpResponse
from user.models import userdata,Address1,Address2
from cart.models import Cart
from product.models import products
from .models import Checkout_list,Order_list,OrderProduct
from django.contrib import messages
from coupons.models import Coupons_info
from decimal import Decimal
import razorpay
from django.views.decorators.csrf import csrf_exempt
from category.models import category
from product.models import products

# Create your views here.
def check_out(request):
    context = {}  # Initialize context with an empty dictionary
    try:
        email = request.session.get('email')
        user = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user=user)
        blocked_offers = Coupons_info.objects.filter(is_active=False)
        offer_info = Coupons_info.objects.exclude(id__in=blocked_offers)

        if not cart_info.exists():
            messages.error(request, "Your cart is empty. Please add products before checking out.")
            return redirect('cart_view')


        out_of_stock_items = []  # List to store out of stock items

        for cart_item in cart_info:
            size = cart_item.selected_size
            if cart_item.product_info.stock_for_size(size) < 1:
                out_of_stock_items.append(cart_item)

        for cart_item in out_of_stock_items:
            cart_item.delete()

        if out_of_stock_items:
            out_of_stock_names = [item.product_info.name for item in out_of_stock_items]
            messages.error(request, f"The following items are out of stock: {', '.join(out_of_stock_names)}")
            return redirect('cart_view')


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

        if amount > 0:
            messages.success(request, f"You have saved an amount of ₹{amount}.")
        
        add1 = Address1.objects.filter(user=user)
        add2 = Address2.objects.filter(user=user)

        # Calculate the subtotal for each item in the cart_info queryset
        sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping = 100
        total_amount = sub_total - amount + shipping

        context = {
            'cart_info': cart_info,
            'sub_total': sub_total,
            'add1': add1,
            'add2': add2,
            'shipping': shipping,
            'offer_info': offer_info,
            'total_offer_saved': amount,
            'total_amount': total_amount,
        }
    except Exception as e:
        messages.error(request, f'Error occurred during checkout: {str(e)}')

    return render(request, 'user_panal/checkout.html', context)

def place_order(request):
    try:
        email = request.session.get('email')
        user_data = userdata.objects.get(email=email)
    
        cart_info = Cart.objects.filter(user=user_data)

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


        amount = max(total_offer_saved, total_product_offer_saved)

        
        if amount > 0:
            pass
                
        # Calculate the subtotal for each item in the cart_info queryset
        sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping = 100
        total_amount = sub_total - amount + shipping

        request.session['subtotal'] = str(sub_total)  # Convert Decimal to string
        request.session['total_amount'] = str(total_amount)  # Convert Decimal to string
        request.session['amount'] = str(amount)

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
            
                return redirect('payment_selection')  # Redirect to payment selection page
            else:
                messages.error(request,"Please select either 'Billing' or 'Shipping' option.")
            # If no checkbox is selected, stay on the current page without saving the order
            return redirect('check_out')
    
        messages.error(request,"Please select either 'Billing' or 'Shipping' option.")
    except Exception as e:
        messages.error(request, f'Error occurred during checkout: {str(e)}')
    return redirect('check_out')  # Redirect if request method is not POST

def payment_selection(request):
    email = request.session.get('email')
        
    user = userdata.objects.get(email=email)
    cart_info = Cart.objects.filter(user=user)

    subtotal = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
    shipping_charge = Decimal('100')  # Convert to Decimal
    total = subtotal + shipping_charge
    context = {'total':total}
    return render(request,'user_panal/payment_method.html',context)

def cod(request):
    try:
        email = request.session.get('email')
        user_data = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user=user_data)

        address = request.session['billing_address']
        total_amount = request.session['total_amount']
        offer = request.session['amount']
        locality = request.session['billing_locality']
        pincode = request.session['billing_pincode']
        district = request.session['billing_district']
        state = request.session['billing_state']

        order_instance = Order_list(
                    user=user_data,
                    total_amount=total_amount,
                    offer=offer,
                    billing_address=address,
                    billing_locality=locality,
                    billing_pincode=pincode,
                    billing_district=district,
                    billing_state=state,)
        order_instance.save()

        for cart_item in cart_info:
                OrderProduct.objects.create(
                user=user_data,
                order=order_instance,
                product_name=cart_item.product_info.name,
                code = cart_item.product_info.code,
                category_info = cart_item.product_info.product_type.name,
                quantity=cart_item.quantity,
                selected_size = cart_item.selected_size,
                price=cart_item.product_info.price,
                offer=cart_item.product_info.offer
            )

        for cart_item in cart_info:
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
        messages.error(request, f'Error occurred during checkout: {str(e)}')
    return redirect('check_out_success')


def razorpay_payment(request):
    email = request.session.get('email')
    if email is None:
        return redirect('checkout')  # Redirect to checkout page if email is not in session
    
    try:
        user = userdata.objects.get(email=email)
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


        amount = max(total_offer_saved, total_product_offer_saved)

        subtotal = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping_charge = Decimal('100')  # Convert to Decimal
        total = subtotal + shipping_charge-amount

        amount = total  # Example amount in paise, change as per your requirement
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
        return render(request, "user_panal/razorpay.html", context)
    except userdata.DoesNotExist:
        messages.error(request, 'Customer not found.')
    except Exception as e:
        messages.error(request, f'Razorpay payment failed: {str(e)}')
    
    return redirect('check_out') 


@csrf_exempt
def handle_razorpay_success(request):
    if request.method == "POST":
        # Extract payment information from the POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        email = request.POST.get('email')


        # Add your logic to mark the order as paid or any other necessary actions
        # For example, create a new order and save it to the database
        try:
            user_data = userdata.objects.get(email=email)   
        except userdata.DoesNotExist:
            return HttpResponse('Invalid email', status=400)  # Return a 400 response for an invalid emai
        
        # Render the success template with context data
        return render(request, 'user_panal/order_succes.html')
    else:
        return render(request, 'user_panal/checkout.html')
    
def razorpay_payment_success(request):
        try:
            email = request.session.get('email')
        
            user = userdata.objects.get(email=email)
            cart_info = Cart.objects.filter(user=user)

            subtotal = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
            shipping_charge = Decimal('100')  # Convert to Decimal
            total = subtotal + shipping_charge

            address = request.session['billing_address']
            total_amount = request.session['total_amount']
            offer = request.session['amount']
            locality = request.session['billing_locality']
            pincode = request.session['billing_pincode']
            district = request.session['billing_district']
            state = request.session['billing_state']

            order_instance = Order_list(
                    user=user,
                    total_amount=total_amount,
                    offer=offer,
                    billing_address=address,
                    billing_locality=locality,
                    billing_pincode=pincode,
                    billing_district=district,
                    billing_state=state,
                    payment_status="Amount is paid", 
                    payment_method="Online banking")
            order_instance.save()


            for cart_item in cart_info:
                OrderProduct.objects.create(
                user=user,
                order=order_instance,
                product_name=cart_item.product_info.name,
                code = cart_item.product_info.code,
                category_info = cart_item.product_info.product_type.name,
                quantity=cart_item.quantity,
                selected_size = cart_item.selected_size,
                price=cart_item.product_info.price,
                offer=cart_item.product_info.offer
            )

            for cart_item in cart_info:
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


def check_out_success(request):
    return render(request,'user_panal/check_out_success.html')

@csrf_exempt
def razorpay_success(request):
    return render(request,'user_panal/razorpay_payment_success.html')

def coupan_offers(request):
    try:
        offers = Coupons_info.objects.all()
        context = {'offers':offers}
    except Exception as e:
        messages.error(request, f'Failed to retrieve coupon offers: {str(e)}')
    return render(request, 'user_panal/checkout.html', context)
    
def order_in_detail(request, id):
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
    return render(request, 'user_panal/order_in_detail.html', context)


