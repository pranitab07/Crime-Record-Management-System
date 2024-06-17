from django.shortcuts import render,redirect
from django.contrib.auth.models import User as U
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import User
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
from collections import Counter

plt.switch_backend('Agg')

def start(request):
    if request.method=='POST':
        name=request.POST.get('name')
        em=request.POST.get('email')
        umess=request.POST.get('message')
        customer=contactus(c_name=name,c_email=em,c_message=umess)
        customer.save()
    return render(request,'start.html')


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

def login_citizens(request):
     if request.method=='POST':
        username=request.POST.get('username')
        pass11=request.POST.get('pass')
        user=authenticate(request, username=username,password=pass11)
        if user is not None:
           auth_login(request,user)
           fname=request.user.first_name
           model_count=User.objects.filter(user=request.user).count()
           return render(request,'home.html',{'total_count': model_count,'name':fname})
        else:
            message="Username or password is incorrect."
            return render(request, 'index1.html', {'login_failed_message': message})

     return render(request,'index1.html')

def login_police(request):
     if request.method=='POST':
        username=request.POST.get('police_id')
        pass11=request.POST.get('pass')

        Police=authenticate(request, username=username,password=pass11)
        if Police is not None and Police.is_superuser:
           auth_login(request,Police)
           reversed_data = User.objects.order_by('created_at').reverse()[:5]
           total_records = User.objects.count()
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
           data_dict={'data':reversed_data,'total_count':total_records,'city_count':city_counts.count(),'city':city_counts,'month_count':month_c}
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
    data= User.objects.raw("  SELECT * FROM newprojectschema.use  ORDER BY id DESC LIMIT  1")
    return render(request, 'c_fir.html',{'data': data})

def analyze_data(request):
    #all charts
    queryset = User.objects.all()
    df= pd.DataFrame(list(queryset.values()))
    df = df.reset_index()

    #pie chart
    crimes = User.objects.all()
    city_count = Counter(crime.ccity for crime in crimes)
    labels = list(city_count.keys())
    sizes = list(city_count.values())
    colors = plt.cm.Paired(range(len(labels)))
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    #plt.title('Citywise Crime Analysis')
    st2_path='static/plots/pie.png'
    plt.savefig(st2_path)
    plt.close()


    #bar plot
    month_count = Counter(datetime.strptime(crime.cdateincident, '%Y-%m-%d').strftime('%B') for crime in crimes)
    
    labels = list(month_count.keys())
    sizes = list(month_count.values())
    plt.figure(figsize=(10, 6))
    plt.bar(labels, sizes,color='magenta')
    plt.xlabel('Months')
    plt.ylabel('Number of Crimes')
    plt.title('Month-wise Crime Analysis (Bar Chart)')
    st_path='static/plots/bar1.png'
    plt.savefig(st_path)
    plt.close()


    #histogram plot
    nationality_count = Counter(crime.cnationality for crime in crimes)
    
    labels = list(nationality_count.keys())
    sizes = list(nationality_count.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(labels, sizes, color='skyblue')
    plt.xlabel('Nationality')
    plt.ylabel('Number of Crimes')
    plt.title('Nationality-wise Crime Analysis (Histogram)')
    plt.xticks(rotation=45, ha='right')
    st3_path='static/plots/histo.png'
    plt.savefig(st3_path)
  
    context={'bar1' : st_path,'histo':st3_path,'pie':st2_path}
    return render(request, 'analysis_result.html',context)

@login_required(login_url='login/citizens')
def home(request):
    fname=request.user.first_name
    model_count=User.objects.filter(user=request.user).count()
    return render(request,'home.html',{'total_count': model_count,'name':fname})

@login_required(login_url='login/police')
def home_police(request):
    return render(request,'home_police.html')