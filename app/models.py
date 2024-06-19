from django.db import models
from django.contrib.auth.models import User
from .models import User as u
# Create your models here.


class User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    cname=models.CharField(max_length=100)
    cdob=models.CharField(max_length=15)
    ccity=models.CharField(max_length=50)
    caddress=models.CharField(max_length=500)
    ccontact=models.CharField(max_length=15)
    cnationality=models.CharField(max_length=20)
    cdateincident=models.CharField(max_length=20)
    clocation=models.CharField(max_length=100)
    cdetails=models.CharField(max_length=500)
    a_r=models.BooleanField(null=True,blank=True)
    remark=models.TextField(max_length=100,null=True,blank=True)

    class Meta:
        db_table="use"


class contactus(models.Model):
    c_name=models.CharField(max_length=100)
    c_email=models.CharField(max_length=100)
    c_message=models.CharField(max_length=100)

    class Meta:
        db_table="contactus"

class charge_sheet(models.Model):
    main_user=models.CharField(max_length=100,null=True,blank=True,unique=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    law=models.CharField(max_length=100,null=True,blank=True)
    officer=models.CharField(max_length=100,null=True,blank=True)
    investigation=models.TextField(max_length=200,null=True,blank=True)
    t_f=models.BooleanField(default=False)

    class Meta:
        db_table="charge_sheet"