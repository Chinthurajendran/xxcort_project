from django.urls import path
from.import views

urlpatterns = [ 
    path('generate_monthly_data', views.generate_monthly_data, name='generate_monthly_data'),
    path('generate_yearly_data', views.generate_yearly_data, name='generate_yearly_data'),
]