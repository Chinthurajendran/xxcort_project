from django.db import models
from user.models import userdata 


# Create your models here.

class Coupons_info(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class Coupons_User(models.Model):
    user = models.ForeignKey(userdata, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupons_info, on_delete=models.CASCADE)
    date_used = models.DateTimeField(auto_now_add=True)


class Reference_coupon(models.Model):
    user = models.ForeignKey(userdata, on_delete=models.CASCADE)
    reference_coupon_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2,default=500)
    date = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


# class Reference(models.Model):
#     user = models.ForeignKey(userdata, on_delete=models.CASCADE)
#     reference_code = models.ForeignKey(Reference_coupon, on_delete=models.CASCADE)