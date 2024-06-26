from django.shortcuts import render,redirect
from product.models import products
from category.models import category
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def new_collection(request):
    try:
        products_count = products.objects.count()
        blocked_product = products.objects.filter(is_active=False)
        
        # Filter by selected category
        selected_category_ids = request.GET.getlist('category_id')  # Get list of selected categories
        if selected_category_ids:
            collections = products.objects.filter(product_type__in=selected_category_ids).exclude(id__in=blocked_product).order_by('name')
        else:
            collections = products.objects.exclude(id__in=blocked_product).order_by('name')
        
        # Sorting
        sort_by = request.GET.get('sort_by')
        if sort_by == 'price_asc':
            collections = collections.order_by('price')
        elif sort_by == 'price_desc':
            collections = collections.order_by('-price')
        elif sort_by == 'name_asc':
            collections = collections.order_by('name')
        elif sort_by == 'name_desc':
            collections = collections.order_by('-name')
        # Add more sorting options if needed
        
        data = category.objects.all()

        # Pagination
        paginator = Paginator(collections, 4)  # 4 products per page
        page = request.GET.get('page')
        try:
            collections = paginator.page(page)
        except PageNotAnInteger:
            collections = paginator.page(1)
        except EmptyPage:
            collections = paginator.page(paginator.num_pages)

        num = products_count
        context = {'collections': collections, 'data': data, 'num': num}
    except Exception as e:
        messages.error(request, f'Failed to load new collection: {str(e)}') 
    return render(request, 'user_panal/new_collection.html', context)






