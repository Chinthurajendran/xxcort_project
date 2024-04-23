from django.shortcuts import render,redirect
from.models import category
from django.shortcuts import get_object_or_404
from django.contrib import messages
from product.models import products

# Create your views here.

def product_type(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    data = category.objects.all()
    return render(request, 'admin_panal/product_type.html',{'data':data})

def product_type_edit(request, id):
    if 'username' not in request.session:
        return redirect('admin_login')

    try:
        category_data = category.objects.get(id=id)

        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('message')
            offer = request.POST.get('category_offer')

            category_instance = category.objects.get(id=id)
            category_instance.name = name
            category_instance.description = description
            category_instance.offer = offer
            category_instance.save()

            messages.success(request, 'Category updated successfully.')
            return redirect('product_type')

    except category.DoesNotExist:
        messages.error(request, 'Category does not exist.')

    except Exception as e:
        messages.error(request, f'Failed to update category: {str(e)}')

    return render(request, 'admin_panal/product_type_edit.html', {'category_data': category_data})



def product_type_create(request):
    if 'username' not in  request.session:
        return redirect('admin_login')
    massage = None
    try:
        if request.method == 'POST':
            category_name = request.POST.get('name')
            category_description = request.POST.get('message')
            offer = request.POST.get('category_offer')
            if category.objects.filter(name = category_name).exists():
                massage = 'PRODUCT AREADY CREATED'
            else:
                data = category(name = category_name,description = category_description,offer =offer)
                data.save()
                messages.success(request, 'Category created successfully.')
                return redirect('product_type')
    except Exception as e:
        messages.error(request, f'Failed to create category: {str(e)}')
    return render(request, 'admin_panal/product_type_create.html',{'massage':massage})

def product_type_delete(request,id):
    try:
        data = category.objects.get(id=id)
        data.delete()
        messages.success(request, 'Category deleted successfully.')
    except Exception as e:
        messages.error(request, f'Failed to delete category: {str(e)}')
    return redirect('product_type')

def category_block_user(request,user_id):
    try:
        user = get_object_or_404(category, id=user_id)

    # Toggle the blocked field
        user.is_active = not user.is_active
        user.save()

        messages.success(request, f'{user.name} has been {"blocked" if user.is_active else "unblocked"}.')
    except Exception as e:
        messages.error(request, f'Failed to block/unblock category: {str(e)}')
    return redirect('product_type')


def collection_sort(request,id):
    try:
        category_info  = category.objects.get(id=id)
        products_count = products.objects.filter(product_type = category_info).count()
        blocked_categories = category.objects.filter(is_active = False)
        blocked_product = products.objects.filter(is_active = False)
        collections = products.objects.exclude(product_type__in = blocked_categories).exclude(id__in=blocked_product).filter(product_type = category_info)
        data = category.objects.all()
        num = products_count
        context = {'collections':collections,'data':data,'num':num}
    except Exception as e:
        messages.error(request, f'Failed to load new collection: {str(e)}') 
    return render(request,'user_panal/new_collection.html',context)

def categorys (request):
    try:
        products_count = products.objects.count()
        blocked_categories = category.objects.filter(is_active = False)
        blocked_product = products.objects.filter(is_active = False)
        collections = products.objects.exclude(product_type__in = blocked_categories).exclude(id__in=blocked_product).all()
        data = category.objects.all()
        num = products_count
        context = {'collections':collections,'data':data,'num':num}
    except Exception as e:
        messages.error(request, f'Failed to load new collection: {str(e)}') 
    return render(request,'user_panal/new_collection.html',context)