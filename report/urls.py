from django.urls import path
from . import views

urlpatterns = [
	# path('venue_pdf', views.venue_pdf, name='venue_pdf'),
    # path('pdf_report', views.pdf_report, name='pdf_report'),
    # path('report', views.report, name='report'),
    
    path('sales-report/',views.SalesReportView.as_view(), name='sales-report'),

    # path('generateinvoice/<int:pk>/', views.GenerateInvoice.as_view(), name = 'generateinvoice'),
    # path('generateinvoice/<int:pk>/', views.GenerateInvoice.as_view(), name = 'generateinvoice'),
    path('generate-invoice/<int:pk>/', views.GenerateInvoice.as_view(), name='generateinvoice'),
    
]