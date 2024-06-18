from django.shortcuts import render,redirect
from django.contrib.auth.models import User as U
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import User,charge_sheet
from .models import contactus
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import Cast ,  Substr
from django.db.models import IntegerField
from django.contrib import messages
from .forms import ChargeSheetForm

plt.switch_backend('Agg')

def start(request):
    if request.method=='POST':
        name=request.POST.get('name')
        em=request.POST.get('email')
        umess=request.POST.get('message')
        customer=contactus(c_name=name,c_email=em,c_message=umess)
        customer.save()
    return render(request,'start.html')

@login_required(login_url='login/police')
def accept(request,pk):
    inst=User.objects.get(id=pk)
    inst.a_r=True
    inst.save()
    return home_police(request)

@login_required(login_url='login/police')
def reject(request,pk):
    inst=User.objects.get(id=pk)
    inst.a_r=False
    inst.save()
    return home_police(request)

@login_required(login_url='login/police')
def complete_charge_sheet(request, pk):
    if request.method=='POST':
        form = ChargeSheetForm(request.POST)
        if form.is_valid():
            law=form.cleaned_data["law"]
            officer=form.cleaned_data["officer"]
            investigation=form.cleaned_data["investigation"]
            if not (law==None and officer==None and investigation==None):
                charge=charge_sheet(law=law,officer=officer,investigation=investigation,main_user=pk,t_f=True)
                charge.save()
            return redirect('home_police')
        return redirect('home_police')
    else:
        form = ChargeSheetForm(use_required_attribute=True)
        data_dict={'form':form}
        return render(request,'test.html',data_dict)

@login_required(login_url='login/citizens')
def charge_citizen(request,pk):
    if request.method == 'POST':
        return redirect('home')
    fir=User.objects.filter(id=pk)
    sheet=charge_sheet.objects.filter(main_user=str(pk))
    context={'fir':fir,'sheet':sheet}
    return render(request,'charge_sheet.html',context)

@login_required(login_url='login/police')
def charge(request,pk):
    if request.method == 'POST':
        return redirect('home_police')
    fir=User.objects.filter(id=pk)
    sheet=charge_sheet.objects.filter(main_user=str(pk))
    context={'fir':fir,'sheet':sheet}
    return render(request,'charge_sheet.html',context)

def signup(request):

    if request.method=='POST':
        fname=request.POST.get('fname')
        lname=request.POST.get('lname')
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        us=U.objects.filter(username=uname)
        if us.exists():
            message="Username already exists"
            return render(request,'signup.html', {'signup_failed': message})
        my_user=U.objects.create_user(uname,email,pass1)
        my_user.first_name=fname
        my_user.last_name=lname
        my_user.save()
        return redirect('login_citizens')


    return render(request,'signup.html')

def get_user(data,charge):
    result=[]
    p=[]
    ch={'id':[]}
    for c in charge:
        ch['id'].append(c.main_user)
    for i in data:
        if i.a_r and i.id not in ch['id']:
            if str(i.id) in ch['id']:
                result.append(i.id)
            else:
                p.append(i.id)
                result.append(i.id)
    r=User.objects.filter(id__in=result).order_by('created_at').reverse()
    return r,p

def login_citizens(request):
     if request.method=='POST':
        username=request.POST.get('username')
        pass11=request.POST.get('pass')
        user=authenticate(request, username=username,password=pass11)
        if user is not None:
           auth_login(request,user)
           fname=request.user.first_name
           hist=User.objects.filter(user=request.user).order_by('created_at').reverse()
           charge=charge_sheet.objects.all()
           sheet,pk=get_user(hist,charge)
           model_count=User.objects.filter(user=request.user).count()
           pending=User.objects.filter(user=request.user,a_r=False).count()
           data={'pk':pk,'sheet':sheet,'sheet_count':sheet.count(),'charge':charge,'total_count': model_count,'name':fname,'pending':pending,'history':hist}
           return render(request,'home.html',data)
        else:
            message="Username or password is incorrect."
            return render(request, 'index1.html', {'login_failed_message': message})

     return render(request,'index1.html')

def incomplete_data(data,charge):
    result=[]
    ch=[]
    for c in charge:
        ch.append(c.main_user)
    for row in data:
        if row.a_r and str(row.id) not in ch :
            result.append(row.id)
    
    cha=User.objects.filter(id__in=result)
    return cha

def login_police(request):
    if request.method=='POST':
        username=request.POST.get('police_id')
        pass11=request.POST.get('pass')

        Police=authenticate(request, username=username,password=pass11)
        if Police is not None and Police.is_superuser:
           auth_login(request,Police)
           reversed_data = User.objects.order_by('created_at').reverse()
           total_records = User.objects.count()
           city_counts = User.objects.values('ccity').annotate(total_users=Count('id')).order_by('ccity')
           charge=charge_sheet.objects.all()
           incomplete_sheet=incomplete_data(reversed_data,charge)
           month_counts = (
                User.objects
                .annotate(
                    month=Cast(Substr('cdateincident', 6, 2), IntegerField()) 
                )
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month')
            )
           today = datetime.now()
           current_month = today.month
           month_c=0
           for c in month_counts:
               if(c['month']==current_month):
                   month_c=c['count']
           data_dict={'incomplete':incomplete_sheet,'charge':charge,'data':reversed_data,'total_count':total_records,'city_count':city_counts.count(),'city':city_counts,'month_count':month_c}
           return render(request,'home_police.html',data_dict)
        else:
            message="Police ID or password is incorrect."
            return render(request, 'police_login.html', {'login_failed_message': message})

    return render(request,'police_login.html')

def logout_view(request):
    if request.method=='POST':
        print("yes-logging out")
        logout(request)
        return redirect('login_citizens')
    logout(request)
    return redirect('login_citizens')

def logout_police(request):
    logout(request)
    return redirect('login_police')

def insertuser(request):
    if request.method=='POST':
        u=request.user
        sn=request.POST.get('complainant_name')
        sd=request.POST.get('dob')
        sc=request.POST.get('district')
        sa=request.POST.get('complainant_address')
        st=request.POST.get('complainant_contact')
        so=request.POST.get('nationality')
        si=request.POST.get('incident_date')
        sl=request.POST.get('incident_location')
        se=request.POST.get('incident_details')     

        us=User(user=u,cname=sn,cdob=sd,ccity=sc,caddress=sa,ccontact=st,cnationality=so,cdateincident=si,clocation=sl,cdetails=se)
        us.save()
        return redirect('retrievedata')
    
    return render(request,'index1.html')

def retrieve_data(request):
    if request.method=='POST':
        return redirect('home')
    fir= User.objects.raw("  SELECT * FROM crime_data.use  ORDER BY id DESC LIMIT  1")
    return render(request, 'charge_sheet.html',{'fir': fir,'citizen':True})

def analyze_data(request):
    queryset = User.objects.all()
    df= pd.DataFrame(list(queryset.values()))
    df = df.reset_index()
    plt.hist(df['id'], bins=30, alpha=0.5, color='blue')
    st_path='static/plots/hist.png'
    plt.savefig(st_path)
    #plt.show()

    plt.bar(df['id'],df['id'])
    st1_path='static/plots/bar.png'
    plt.savefig(st1_path)
  
    context={'chart' : st_path,'bar':st1_path}
    return render(request, 'analysis_result.html',context)

@login_required(login_url='login/citizens')
def home(request):
    hist=User.objects.filter(user=request.user).order_by('created_at').reverse()
    charge=charge_sheet.objects.all()
    sheet,pk=get_user(hist,charge)
    fname=request.user.first_name
    pending=User.objects.filter(user=request.user,a_r=False).count()
    model_count=User.objects.filter(user=request.user).count()
    data={'pk':pk,'sheet':sheet,'sheet_count':sheet.count(),'charge':charge,'total_count': model_count,'name':fname,'pending':pending,'history':hist}
    return render(request,'home.html',data)

@login_required(login_url='login/police')
def home_police(request):
    reversed_data = User.objects.order_by('created_at').reverse()
    total_records = User.objects.count()
    charge=charge_sheet.objects.all()
    incomplete_sheet=incomplete_data(reversed_data,charge)
    city_counts = User.objects.values('ccity').annotate(total_users=Count('id')).order_by('ccity')
    month_counts = (
        User.objects
        .annotate(
            month=Cast(Substr('cdateincident', 6, 2), IntegerField()) 
        )
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    today = datetime.now()
    current_month = today.month
    month_c=0
    for c in month_counts:
        if(c['month']==current_month):
            month_c=c['count']
    data_dict={'case': 'i_charge_sheet','incomplete':incomplete_sheet,'charge':charge,'data':reversed_data,'total_count':total_records,'city_count':city_counts.count(),'city':city_counts,'month_count':month_c}
    return render(request,'home_police.html',data_dict)