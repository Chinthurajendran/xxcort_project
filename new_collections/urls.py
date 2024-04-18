from django.urls import path
from.import views

urlpatterns = [
    path('new_collection/', views.new_collection, name='new_collection'),

]
   


