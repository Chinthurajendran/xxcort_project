from django.shortcuts import render,redirect
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter,landscape
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.views import View
from django.db.models import Sum
from checkout.models import Order_list,OrderProduct
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from decimal import Decimal

from coupons.models import Coupons_info,Coupons_User    
from datetime import datetime, timedelta,time
import xlsxwriter

class SalesReportView(View):
    def generate_report(self, start_date, end_date):
        # For daily report
        if start_date == end_date:
            start_of_day = datetime.combine(start_date.date(), time.min)  # Beginning of the day
            end_of_day = datetime.combine(start_date.date(), time.max)  # End of the day

            daily_orders = Order_list.objects.filter(order_date__range=(start_of_day, end_of_day))
            daily_revenue = daily_orders.filter(order_status="Delivered").aggregate(Sum('total_amount'))['total_amount__sum'] or 0

            # Calculate total discount amount and discount count for the day
            blocked_categories = Order_list.objects.exclude(coupon='No Coupon')
            weekly_orders_without_coupons = blocked_categories.filter(order_date__range=[start_of_day, end_of_day])
            daily_discount_amount = Decimal(0)
            for order in weekly_orders_without_coupons:
                # Parse the coupon value and convert it to Decimal
                discount_amount = Decimal(order.coupon)
                daily_discount_amount += discount_amount

            daily_discount_count = Coupons_info.objects.all().count()

            params = {
                "orders":daily_orders,
                'daily_orders_count': daily_orders.count(),
                'daily_revenue': daily_revenue,
                'daily_discount_amount': daily_discount_amount,
                'daily_discount_count': daily_discount_count,
            }

        # For weekly report
        elif (end_date - start_date).days == 6:

            weekly_orders =Order_list.objects.filter(order_date__range=[start_date, end_date])
            completed_weekly_orders = weekly_orders.filter(order_status="Delivered")
            # Calculate weekly revenue
            weekly_revenue = completed_weekly_orders.aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
            
            # Calculate weekly discount amount
           
            blocked_categories = Order_list.objects.exclude(coupon='No Coupon')
            weekly_orders_without_coupons = blocked_categories.filter(order_date__range=[start_date, end_date])
            weekly_discount_amount = Decimal(0)

            for order in weekly_orders_without_coupons:
                # Parse the coupon value and convert it to Decimal
                discount_amount = Decimal(order.coupon)
                weekly_discount_amount += discount_amount

            weekly_discount_count =Coupons_User.objects.filter(date_used__date__range=[start_date, end_date]).count()


            params = {
                "orders":weekly_orders,
                'weekly_orders_count': weekly_orders.count(),
                'weekly_revenue': weekly_revenue,
                'weekly_discount_amount': weekly_discount_amount,
                'weekly_discount_count': weekly_discount_count
            }


        # For yearly report
        elif start_date.year == end_date.year:
            yearly_orders = Order_list.objects.filter(order_date__year=start_date.year)
            yearly_revenue = yearly_orders.filter(order_status="Delivered").aggregate(Sum('total_amount'))['total_amount__sum'] or 0

            yearly_discount_count = Coupons_info.objects.all().count()

            blocked_categories = Order_list.objects.exclude(coupon='No Coupon')
            # Filter orders within the specified date range and where the coupon is 'No Coupon'
            weekly_orders_without_coupons = blocked_categories.filter(order_date__range=[start_date, end_date])
            yearly_discount_amount = Decimal(0)

            for order in weekly_orders_without_coupons:
                # Parse the coupon value and convert it to Decimal
                discount_amount = Decimal(order.coupon)
                yearly_discount_amount += discount_amount

            params = {
                "orders":yearly_orders,
                'yearly_orders_count': yearly_orders.count(),
                'yearly_revenue': yearly_revenue,
                'yearly_discount_amount': yearly_discount_amount,
                'yearly_discount_count': yearly_discount_count,
            }
        
        else:
            # Handle custom date range here
            custom_orders = Order_list.objects.filter(order_date__range=[start_date, end_date])

            params = {
                "orders":custom_orders,
                'custom_orders_count': custom_orders.count(),
            }

        return params
 
    def render_to_pdf(self, context):
        template = get_template('admin_panal/sales_report.html')
        html = template.render(context)
        pdf_file = BytesIO()
        pisa.pisaDocument(BytesIO(html.encode("UTF-8")), pdf_file, encoding='UTF-8')
        return pdf_file.getvalue()

    def render_to_excel(self, context):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'remove_timezone': True})
        worksheet = workbook.add_worksheet('Sales Report')

        headers = ['Order ID', 'Order Date', 'Total Amount', 'Order Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)



        orders = context['orders']
        for row, order in enumerate(orders, start=1):
            order_date = order.order_date.replace(tzinfo=None)
            date_string = order_date.strftime('%d-%m-%Y')

            worksheet.write(row, 0, order.id)
            worksheet.write(row, 1, date_string)
            worksheet.write(row, 2, order.total_amount)
            worksheet.write(row, 3, order.order_status)

        row = row + 2 if 'row' in locals() else 2
        if 'daily_orders_count' in context:
            worksheet.write(row, 0, 'Number of Daily Orders:')
            worksheet.write(row, 1, context['daily_orders_count'])
            worksheet.write(row + 1, 0, 'Daily Revenue:')
            worksheet.write(row + 1, 1, context['daily_revenue'])
            worksheet.write(row + 2, 0, 'Daily Discount Amount:')
            worksheet.write(row + 2, 1, context['daily_discount_amount'])
            worksheet.write(row + 3, 0, 'Daily Discount Count:')
            worksheet.write(row + 3, 1, context['daily_discount_count'])
        elif 'weekly_orders_count' in context:
            worksheet.write(row, 0, 'Number of Weekly Orders:')
            worksheet.write(row, 1, context['weekly_orders_count'])
            worksheet.write(row + 1, 0, 'Weekly Revenue:')
            worksheet.write(row + 1, 1, context['weekly_revenue'])
            worksheet.write(row + 2, 0, 'Weekly Discount Amount:')
            worksheet.write(row + 2, 1, context['weekly_discount_amount'])
            worksheet.write(row + 3, 0, 'Weekly Discount Count:')
            worksheet.write(row + 3, 1, context['weekly_discount_count'])
        elif 'yearly_orders_count' in context:
            worksheet.write(row, 0, 'Number of Yearly Orders:')
            worksheet.write(row, 1, context['yearly_orders_count'])
            worksheet.write(row + 1, 0, 'Yearly Revenue:')
            worksheet.write(row + 1, 1, context['yearly_revenue'])
            worksheet.write(row + 2, 0, 'Yearly Discount Amount:')
            worksheet.write(row + 2, 1, context['yearly_discount_amount'])
            worksheet.write(row + 3, 0, 'Yearly Discount Count:')
            worksheet.write(row + 3, 1, context['yearly_discount_count'])
        elif 'custom_orders_count' in context:
            worksheet.write(row, 0, 'Number of Custom Orders:')
            worksheet.write(row, 1, context['custom_orders_count'])

        workbook.close()
        output.seek(0)
        return output.getvalue()

 
    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('report_type', 'daily')
        report_format = request.GET.get('format', 'pdf')
        

        # Handle report generation based on both factors
        if report_type == 'daily':
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date
        elif report_type == 'weekly':
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=6)
        elif report_type == 'monthly':
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = datetime(end_date.year, end_date.month, 1)
        elif report_type == 'custom':
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)

        # Convert start_date and end_date to timezone-aware datetime objects
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)

        context = self.generate_report(start_date, end_date)

        if report_format == 'pdf':
            pdf_content = self.render_to_pdf(context)
            response = HttpResponse(pdf_content, content_type='application/pdf')
            filename = "sales_report.pdf"
        else:  # report_format == 'excel'
            excel_content = self.render_to_excel(context)
            response = HttpResponse(excel_content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "sales_report.xlsx"

        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response 


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class GenerateInvoice(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            order_db = Order_list.objects.get(id = pk)     #you can filter using order_id as well
            order_product = OrderProduct.objects.filter(order = order_db)
        except:
            return HttpResponse("505 Not Found")
        data = {
            'order_db':order_db,
            'order_product':order_product,
        }
        pdf = render_to_pdf('user_panal/invoice.html', data)

        # force download
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %(data['order_db'])
            content = "inline; filename='%s'" %(filename)
            #if download:
            content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")