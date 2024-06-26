"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

from user.views import page404 as user_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('user.urls')),
    path('',include('admin_side.urls')), 
    path('',include('category.urls')),
    path('',include('product.urls')),  
    path('',include('new_collections.urls')),  
    path('',include('product_list.urls')),
    path('',include('stock.urls')),
    path('',include('cart.urls')),
    path('',include('checkout.urls')),
    path('',include('user_wishlist.urls')),
    path('', include('coupons.urls')),
    path('', include('wallet.urls')),
    path('', include('report.urls')),
    path('', include('chart.urls')),

    path('accounts/', include('allauth.urls')), 
]

handler404 = user_404

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)