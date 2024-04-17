from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
class userdata(models.Model):
    username=models.CharField(max_length=250)
    password=models.CharField(max_length=250)
    email =models.CharField(max_length=250)
    blocked = models.BooleanField(default = False)
    delete = models.BooleanField(default = False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username


class Address1(models.Model):
    user = models.ForeignKey(userdata, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)
    locality = models.CharField(max_length=20)
    pincode = models.IntegerField()
    district = models.CharField(max_length=14)
    state = models.CharField(max_length=15)

    def __str__(self):
        return self.address

class Address2(models.Model):
    user = models.ForeignKey(userdata, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)
    locality = models.CharField(max_length=20)
    pincode = models.IntegerField()
    district = models.CharField(max_length=14)
    state = models.CharField(max_length=15)

    def __str__(self):
        return self.address