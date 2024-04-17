from django.shortcuts import render
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
from checkout.models import Order_list
import json
from datetime import datetime, timedelta
from django.http import JsonResponse


def generate_monthly_data(request):
    # Dictionary mapping month numbers to month names
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    # Get the date 5 years ago from today
    five_years_ago = datetime.now() - timedelta(days=365 * 5)

    # Initialize data dictionary with all months and 0 counts
    data = {month_name: 0 for month_name in month_names.values()}

    # Generate monthly data for the last 5 years
    monthly_data = Order_list.objects.filter(
        order_status='Delivered',
        order_date__gte=five_years_ago
    ).extra({'month': "EXTRACT(month FROM order_date)"}).values('month').annotate(total=Count('id'))

    # Update data with actual counts for months with orders
    for entry in monthly_data:
        month_number = entry['month']
        month_name = month_names.get(month_number)
        if month_name:
            data[month_name] = entry['total']

    return JsonResponse(data)

def generate_yearly_data(request):
    # Get the range of years from 2020 to the current year (2024)
    years_range = range(2020, datetime.now().year + 1)
    
    # Generate yearly data for the last 5 years
    yearly_data = Order_list.objects.filter(
        order_status='Delivered',
        order_date__year__in=years_range  # Filter orders for years from 2020 to 2024
    ).extra({'year': "EXTRACT(year FROM order_date)"}).values('year').annotate(total=Count('id'))
    
    # Prepare data for the last 5 years
    data = {}
    for year in years_range:
        data[year] = 0  # Initialize with 0 orders
    
    for entry in yearly_data:
        year = int(entry['year'])
        total = entry['total']
        data[year] = total
    
    return JsonResponse(data)




