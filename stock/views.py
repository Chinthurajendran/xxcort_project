# from django.shortcuts import render,redirect
# from django.db.models import Sum
# from stock.models import stock
# from django.contrib import messages

# # Create your views here.

# def stock_list(request):
#     stocks_data = stock.objects.all()
#     for s in stocks_data:
#         s.total = s.total_stock()

#     context = {'stocks': stocks_data}
#     return render(request, 'admin_panal/stock_list.html', context)

# def stock_create(request):
#     if request.method == "POST":
#         product_name = request.POST['product_name']
#         product_code = request.POST['product_code']
#         Small = int(request.POST.get('Small', 0))
#         Medium = int(request.POST.get('Medium', 0))
#         Large = int(request.POST.get('Large', 0))
#         Extra_Large = int(request.POST.get('Extra_Large', 0))
#         total = Small+Medium+Large+Extra_Large
#         stock_data = stock(product_name = product_name,
#                            product_code = product_code,
#                            small=Small,medium=Medium,large=Large,extra_Large=Extra_Large,Total_stock = total)
        
#         # stock_data.calculate_total_stock()
#         stock_data.save()

#         return redirect('stock_list')
#     messages.success(request, 'Stock created successfully.')
#     return render(request,'admin_panal/stock_create.html')

# def stock_edit(request,id):
#     stock_info = stock.objects.get(id=id)
#     context = {'stock_info':stock_info}
#     if request.method == "POST":
#         product_name = request.POST['product_name']
#         product_code = request.POST['product_code']
#         Small = int(request.POST.get('Small', 0))
#         Medium = int(request.POST.get('Medium', 0))
#         Large = int(request.POST.get('Large', 0))
#         Extra_Large = int(request.POST.get('Extra_Large', 0))
#         total = Small+Medium+Large+Extra_Large

#         edit = stock.objects.get(id=id)
#         edit.product_name = product_name
#         edit.product_code = product_code
#         edit.small = Small
#         edit.medium = Medium
#         edit.large = Large
#         edit.extra_Large = Extra_Large
#         edit.total_stock = total
#         edit.save()
#         messages.success(request, 'Stock updated successfully.')
#         return redirect('stock_list')

#     return render(request,'admin_panal/stock_edit.html',context)

# def stock_delete(request,id):
#     stock_del = stock.objects.get(id=id)
#     stock_del.delete()
#     messages.success(request, 'Stock deleted successfully.')
#     return redirect('stock_list')


