from django.urls import path
from . import views

urlpatterns = [
    path('sales-report/',views.SalesReportView.as_view(), name='sales-report'),
    path('generate-invoice/<int:pk>/', views.GenerateInvoice.as_view(), name='generateinvoice'),
    
]