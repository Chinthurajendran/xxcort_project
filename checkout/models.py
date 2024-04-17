from django.db import models
from user .models import userdata
from django.utils import timezone

# Create your models here.
class Checkout_list(models.Model):
    user = models.ForeignKey(userdata,on_delete =models.CASCADE)
    subtotal=models.DecimalField(max_digits=10, decimal_places=2)

class Order_list(models.Model):
    user = models.ForeignKey(userdata,on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places = 2)
    payment_status = models.CharField(max_length=20,default="Pending")
    payment_method = models.CharField(max_length = 15,default="COD")
    order_status = models.CharField(max_length = 15, default = "Pending" )
    order_date = models.DateTimeField(auto_now_add=True)
    coupon=models.CharField(max_length=15, default="No Coupon")
    offer=models.CharField(max_length=15, default="No offer")
    reason = models.CharField(max_length=50, null=True)
    current_status = models.CharField(max_length = 15, default = "Pending" )


      # Billing Address fields
    billing_address = models.CharField(max_length=50)
    billing_locality = models.CharField(max_length=20)
    billing_pincode = models.IntegerField()
    billing_district = models.CharField(max_length=14)
    billing_state = models.CharField(max_length=15)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    

class OrderProduct(models.Model):
    user = models.ForeignKey(userdata,on_delete=models.CASCADE)
    order = models.ForeignKey(Order_list, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True)
    category_info = models.CharField(max_length=100, null=True)
    selected_size = models.CharField(max_length=10, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer = models.IntegerField(default = None)

