from django.db import models

# Create your models here.


class User(models.Model):
    cname=models.CharField(max_length=100)
    cdob=models.CharField(max_length=15)
    ccity=models.CharField(max_length=50)
    caddress=models.CharField(max_length=500)
    ccontact=models.CharField(max_length=15)
    cnationality=models.CharField(max_length=20)
    cdateincident=models.CharField(max_length=20)
    clocation=models.CharField(max_length=100)
    cdetails=models.CharField(max_length=500)


    class Meta:
        db_table="use"


class contactus(models.Model):
    c_name=models.CharField(max_length=100)
    c_email=models.CharField(max_length=100)
    c_message=models.CharField(max_length=100)

    class Meta:
        db_table="contactus"
