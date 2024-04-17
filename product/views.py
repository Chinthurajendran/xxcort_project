from django.shortcuts import render,redirect
from.models import products
from category.models import category
from decimal import Decimal 
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def admin_product_info(request):
        product_lists = products.objects.all()
        return render(request, 'admin_panal/product_info.html',{'product_lists':product_lists})

def admin_product_info(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    # Filter out categories that are not blocked
    blocked_categories = category.objects.filter(is_active=False)
    
    # Get products that belong to non-blocked categories
    product_lists = products.objects.exclude(product_type__in=blocked_categories)

    # Pagination
    paginator = Paginator(product_lists, 4)  # 4 products per page
    page = request.GET.get('page')
    try:
        product_lists = paginator.page(page)
    except PageNotAnInteger:
        product_lists = paginator.page(1)
    except EmptyPage:
        product_lists = paginator.page(paginator.num_pages)
    
    return render(request, 'admin_panal/product_info.html', {'product_lists': product_lists})

def admin_product_info_create(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        product_categorys = category.objects.filter(is_active = True)
        context = {
        'product_category':product_categorys}
        if request.method == 'POST':
            product_id = request.POST['product']
            name = request.POST['product_name']
            code = request.POST['product_code']
            small = int(request.POST.get('small', 0))
            medium = int(request.POST.get('medium', 0))
            large = int(request.POST.get('large', 0))
            # stock_in = request.POST['product_stock']
            stock_in = small+medium+large
            description = request.POST['product_description']
            price = Decimal(request.POST['price'])
            image1 = request.FILES['image1']
            image2 = request.FILES['image2']
            image3 = request.FILES['image3']
            offer = Decimal(request.POST['offer'])
            offer_price = price-price*offer/100

            if not name:
                messages.error(request, 'Product field cannot be empty.')
            elif not description:
                messages.error(request, 'Description field cannot be empty.')
            elif not price:
                messages.error(request, 'Price field cannot be empty.')
            elif not offer:
                messages.error(request, 'Offer field cannot be empty.')
            elif not image1:
                messages.error(request, 'Image field cannot be empty.')
            elif not image2:
                messages.error(request, 'Image field cannot be empty.')
            elif not image3:
                messages.error(request, 'Image field cannot be empty.')
            else:
                category_info = category.objects.get(id = product_id)
        
                product_data = products( product_type=category_info,
                                    name = name,
                                    product_description= description,
                                    price = price,
                                    image1=image1,
                                    image2=image2,
                                    image3=image3,
                                    offer=offer,
                                    offer_price = offer_price,
                                    code = code,
                                    small =small,
                                    medium =medium,
                                    large = large,
                                    stock=stock_in)
                product_data.save()
                messages.success(request, 'Product created successfully.')
                return redirect('admin_product_info')
    except Exception as e:
        messages.error(request, f'Product creation failed: {str(e)}')
    return render(request, 'admin_panal/product_info_create.html',context)

def admin_product_info_edit(request,id):
    if 'username' not in  request.session:
        return redirect('admin_login')
    try:
        product_details = products.objects.get(id=id)
        product_categorys_edit = category.objects.filter(is_active = True)
        context = {
            'product_categorys_edit':product_categorys_edit,
            'product_details':product_details,
        }

        if request.method == 'POST':
            product_id = request.POST.get('products') 
            small = int(request.POST.get('small', 0))
            medium = int(request.POST.get('medium', 0))
            large = int(request.POST.get('large', 0))
            # stock = request.POST.get('product_stock') 
            stock = small+medium+large
            code = request.POST.get('product_code')
            product_name = request.POST.get('product_name')
            product_description = request.POST.get('product_description')
            price = Decimal(request.POST.get('price'))
            offer = Decimal(request.POST.get('offer'))
            offer_price = price-price*offer/100
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')
            image3 = request.FILES.get('image3')

            product = category.objects.get(id = product_id)
            product_edit=products.objects.get(id=id)
        
            product_edit.product_type = product
            product_edit.name = product_name
            product_edit.code = code
            product_edit.small = small
            product_edit.medium = medium
            product_edit.large = large
            product_edit.stock = stock
            product_edit.product_description = product_description
            product_edit.price = price
            product_edit.offer = offer
            product_edit.offer_price = offer_price
            # Check if images are provided in the form

            if image1:
                product_edit.image1 = image1
            if image2:
                product_edit.image2 = image2
            if image3:
                product_edit.image3 = image3

            product_edit.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_product_info')
    except Exception as e:
        messages.error(request, f'Product update failed: {str(e)}') 
    return render(request, 'admin_panal/product_info_edit.html',context)

def admin_product_info_delete(request, id):
    try:
        delete_product = products.objects.get(id=id)
        delete_product.delete()
        messages.success(request, 'Product deleted successfully.')
    except products.DoesNotExist:
        messages.error(request, 'Product does not exist.')
    except Exception as e:
        messages.error(request, f'Product deletion failed: {str(e)}')
    return redirect('admin_product_info')


def products_block_user(request, user_id):
    try:
        product = get_object_or_404(products, id=user_id)

        # Toggle the blocked field
        product.is_active = not product.is_active
        product.save()

        messages.success(request, f'{product.name} has been {"blocked" if product.is_active else "unblocked"}.')
    except Exception as e:
        messages.error(request, f'Product update failed: {str(e)}')
    return redirect('admin_product_info')

