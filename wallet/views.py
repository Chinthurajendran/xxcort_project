from django.shortcuts import render,redirect
from user.models import userdata
from.models import Wallet,Transaction
import razorpay
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from cart.models import Cart
from django.contrib import messages
from checkout.models import Checkout_list,Order_list,OrderProduct
# Create your views here.


def wallet(request): 
    email = request.session.get('email')
    user = userdata.objects.get(email=email)
    
    try:
        wallet_info = Wallet.objects.get(user = user)
        transactions = Transaction.objects.filter(wallet=wallet_info).order_by('-date_created')
    except Wallet.DoesNotExist:
        # If the user doesn't have a wallet, set wallet and transactions to None
        wallet_info = None
        transactions = None
    context ={'transactions':transactions,
              'wallet_info':wallet_info}
    return render(request, 'user_panal/wallet.html',context)
 

def razorpay_wallet_add(request):
    try:
        if request.method == 'POST':
            email = request.session.get('email')
            user = userdata.objects.get(email=email)
            amount_str = request.POST.get('amount')
    
            amount = Decimal(amount_str.replace(',', ''))
            currency = "INR"

            client = razorpay.Client(auth=("rzp_test_tFO7oGhYPMf1B2", "CHcnMspVfaQAHR4UuhsMXoyP"))

            cash  = client.order.create({
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "payment_capture": '1'  # Auto capture payment
                })
            context = {
                "payment_details": {
                "id": cash ['id'],  # Use the generated order ID
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "key": "rzp_test_tFO7oGhYPMf1B2", 
                "email": email, 
                    }
                }
            return render(request, "user_panal/razorpay_add_cash.html", context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return redirect('wallet')
    
@csrf_exempt
def razorpay_wallet_success(request):
    return render(request,'user_panal/razorpay_wallet_success.html')

@csrf_exempt
def handle_razorpay_wallet_success(request):
    try:
        if request.method == "POST":
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_order_id = request.POST.get('razorpay_order_id')
            email = request.POST.get('email')
            amount = Decimal(request.POST.get('amount'))

            user = userdata.objects.get(email=email)
            wallet, created = Wallet.objects.get_or_create(user=user)

            wallet.balance += amount
            wallet.save()

            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type='Credit'
            )
            transaction.save()

            # You might want to add additional logic here to mark the order as paid or perform other necessary actions
            
            return redirect('razorpay_wallet_success')  # Redirect to success page or render a success template
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    return render(request, 'user_panal/wallet.html')


def razorpay_wallet_payment_success(request):
    email = request.session.get('email')
    if email is None:
        return redirect('check_out')
    try:
        user = userdata.objects.get(email=email)
        cart_info = Cart.objects.filter(user = user)



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

        sub_total = sum(cart_item.quantity * cart_item.product_info.price for cart_item in cart_info)
        shipping = 100
        total = sub_total - amount + shipping

        wallet_info = Wallet.objects.get(user =user)
        wallet_info.balance -= total
        wallet_info.save()

        transation_info =Transaction.objects.create(wallet=wallet_info,
                                                amount = total,
                                                transaction_type = 'Debit')
        transation_info.save()



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
                payment_method="Wallet")
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
        messages.error(request, f'Wallet payment failed: {str(e)}') 
    return redirect('order_details')


def wallet_payment_success(request):
    return render(request,'user_panal/wallet_payment_success.html')



