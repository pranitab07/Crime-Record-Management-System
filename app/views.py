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
from django.contrib.auth import update_session_auth_hash
from .forms import ChargeSheetForm,FIRForm
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

@login_required(login_url='login/police')
def accept(request,pk):
    inst=User.objects.get(id=pk)
    inst.a_r=True
    inst.save()
    return home_police(request)
    

@login_required(login_url='login/police')
def reject(request,pk):
    inst=User.objects.get(id=pk)
    if request.method=='POST':
        form = FIRForm(request.POST)
        if form.is_valid():
            remark=form.cleaned_data["remark"]
            inst=User.objects.get(id=pk)
            inst.a_r=False
            inst.remark=remark
            inst.save()
            print(inst.remark)
            messages.error(request,"FIR was rejected")
            dict_data=police_data()
            return render(request,'home_police.html',dict_data)
    else:
        form = FIRForm()
        data_dict={'form':form}
        return render(request,'test.html',data_dict)


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
    rej=False
    acc=False
    charge_is=False
    s=[]
    for j in sheet:
        s.append(j.main_user)
    for f in fir:
        if not f.a_r:
            rej=True
        if f.a_r:
            acc=True
        if str(f.id) in s:
            charge_is=True

    context={'fir':fir,'sheet':sheet,'rejection':rej,'accepted':acc,'charge_is':charge_is}
    return render(request,'charge_sheet.html',context)

@login_required(login_url='login/police')
def charge(request,pk):
    if request.method == 'POST':
        return redirect('home_police')
    fir=User.objects.filter(id=pk)
    sheet=charge_sheet.objects.filter(main_user=str(pk))
    acc=False
    not_up=False
    charge_is=False
    s=[]
    for j in sheet:
        s.append(j.main_user)
    for f in fir:
        if f.a_r==None:
            not_up=True
        if f.a_r:
            acc=True
        if str(f.id) in s:
            charge_is=True
    context={'fir':fir,'sheet':sheet,'not_up':not_up,'accepted':acc,'charge_is':charge_is}
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
        messages.success(request,"User registered successfully")
        return redirect('login_citizens')


    return render(request,'signup.html')

def get_user(data,charge):
    result=[]
    p=[]
    ch={'id':[]}
    count=0
    for c in charge:
        ch['id'].append(c.main_user)
    for i in data:
        if i.a_r==None:
            count+=1

        if i.a_r and i.id not in ch['id']:
            if str(i.id) in ch['id']:
                result.append(i.id)
            else:
                p.append(i.id)
                result.append(i.id)
    r=User.objects.filter(id__in=result).order_by('created_at').reverse()
    return r,p,count

def citizen_data(request):
    fname=request.user.first_name
    hist=User.objects.filter(user=request.user).order_by('created_at').reverse()
    charge=charge_sheet.objects.all()
    sheet,pk,c=get_user(hist,charge)
    model_count=User.objects.filter(user=request.user).count()
    pending=User.objects.filter(user=request.user,a_r=False).count()
    data={'pk_count':c,'pk':pk,'sheet':sheet,'sheet_count':sheet.count(),'charge':charge,'total_count': model_count,'name':fname,'pending':pending,'history':hist}
    return data

def login_citizens(request):
     if request.method=='POST':
        username=request.POST.get('username')
        pass11=request.POST.get('pass')

        user=authenticate(request, username=username,password=pass11)

        if user is not None:
           auth_login(request,user)
           data=citizen_data(request)
           return render(request,'home.html',data)
        
        else:
            message="Username or password is incorrect."
            return render(request, 'index1.html', {'login_failed_message': message})

     return render(request,'index1.html')

def pie_chart(city_counts,x):
    cities = [entry['ccity'] for entry in city_counts]
    total_users = [entry['total_users'] for entry in city_counts]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c4e17f', '#ff6666', '#3cd9e5', '#c2c2f0']
    explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    plt.figure(figsize=(10, 7))
    plt.pie(total_users, labels=cities, colors=colors[:x], autopct='%1.1f%%', startangle=90, explode=explode[:x], shadow=True)

    plt.title('Top 10 Cities with Highest Number of Cases', fontsize=16, fontweight='bold')

    plt.axis('equal')
    st_path='static/plots/pie1.png'
    plt.savefig(st_path)
    return st_path

def r(data):
    reject=[]
    for d in data:
        if not d.a_r:
            reject.append(d.id)
    return reject

def incomplete_data(data,charge):
    result=[]
    ch=[]
    for c in charge:
        ch.append(c.main_user)
    for row in data:
        if row.a_r and str(row.id) not in ch :
            result.append(row.id)
    
    cha=User.objects.filter(id__in=result).order_by('created_at').reverse()
    return cha

def police_data():
    reversed_data = User.objects.order_by('created_at').reverse()
    total_records = User.objects.count()
    city_counts = User.objects.values('ccity').annotate(total_users=Count('id')).order_by('ccity')
    path=pie_chart(city_counts,city_counts.count())
    charge=charge_sheet.objects.all().order_by('created_at').reverse()
    incomplete_sheet=incomplete_data(reversed_data,charge)
    rejected=r(reversed_data)
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

    new_fir=0
    for i in reversed_data:
        if i.a_r==None:
            new_fir=new_fir+1
    data_dict={'rejected':rejected,'new_fir':new_fir,'incomplete':incomplete_sheet,'charge':charge,'data':reversed_data,'total_count':total_records,'city_count':city_counts.count(),'city':city_counts,'month_count':month_c}
    return data_dict
    
def login_police(request):
    if request.method=='POST':
        username=request.POST.get('police_id')
        pass11=request.POST.get('pass')

        Police=authenticate(request, username=username,password=pass11)

        if Police is not None and Police.is_superuser:
           auth_login(request,Police)
           data_dict=police_data()
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
    data=citizen_data(request)
    return render(request,'home.html',data)

@login_required(login_url='login/police')
def home_police(request):
    data_dict=police_data()
    return render(request,'home_police.html',data_dict)

@login_required(login_url='login/police')
def search(request):
    if request.method=='GET':
        query= request.GET['query']
        a1=User.objects.filter(cname__icontains=query)
        a2=User.objects.filter(clocation__icontains=query)
        a3=User.objects.filter(cdateincident__icontains=query)
        a4=User.objects.filter(cdetails__icontains=query)
        a5=User.objects.filter(ccontact__icontains=query)
        a=a1.union(a2,a3,a4,a5)
        data_dict=police_data()
        data_dict['data'] = a.order_by('created_at').reverse()
        return render(request,'home_police.html',data_dict)
    data_dict=police_data()
    return render(request,'home_police.html',data_dict)

@login_required(login_url='login/citizens')
def profile(request):
    if request.method == 'POST':
        fname = request.POST.get('first_name')
        lname = request.POST.get('last_name')
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = request.user
            user.first_name = fname
            user.last_name = lname
            user.email = email
            if old_password and new_password and confirm_password:
                if user.check_password(old_password):
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        update_session_auth_hash(request, user)
                    else:
                        messages.error(request, 'New passwords do not match.')
                        if user.is_superuser:
                            return redirect('home_police')
                        return redirect('home')
                else:
                    messages.error(request, 'Old password is incorrect.')
                    if user.is_superuser:
                        return redirect('home_police')
                    return redirect('home')
            user.save()
            messages.success(request, 'Your profile was successfully updated!')
            if user.is_superuser:
                return redirect('home_police')
            return redirect('home')
        except:
            messages.error(request,'Something went wrong, Try Again')
            if user.is_superuser:
                return redirect('home_police')
            return redirect('home')
    return render(request,'edit_profile.html')