from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
import random
from .models import *
from app_seller.models import *
from django.db.models import Q
from django.contrib.auth.hashers import make_password,check_password


# Create your views here.
def index(request):
    return render(request,"index.html")

def register(request):
    if request.method=="POST":
        global temp
        temp={
            "name":request.POST["name"],
            "email":request.POST["email"],
            "password":request.POST["pswd"]# pswd =sing-up.html se fild name hai

        }
        global otp
        otp=random.randint(100000,999999)
        subject = 'OTP Verification'
        message = f'Your OTP is. {otp} valid for 5 mintute only'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST["email"],  ]
        send_mail( subject, message, email_from, recipient_list )
        return render(request,"otp.html")
    else:
        return render(request,"sign-up.html")

def otp(request):   
    if request.method=="POST":
        if otp==int(request.POST["otp"]):
            User.objects.create(
                name=temp["name"],
                email=temp["email"],
                password=make_password(temp["password"])

            )
            return render(request,"sign-up.html",{"msg":"registation successfull"})
        else:
            return render(request,"sign-up.html",{"msg":"otp not matched"})


    else: 
        return render(request,"sign-up.html")
    
def login(request):
    if request.method=="POST":
        try:
            User_data = User.objects.get(email = request.POST["email"])
            if check_password(request.POST["Password"],User_data.password):
                request.session["email"]=request.POST["email"]
                return render(request,"shop-list.html")
            else:
                return render(request,"login.html",{"msg":"Password Not Match"})
        except:
            return render(request,"login.html",{"msg":"User not Exist"})
    else:
        return render(request,"login.html")
    
def logout(request):
    del request.session["email"]
    return render(request,"login.html",{"msg":"Logout Successfully"})

def profile(request):
    data=User.objects.get(email=request.session["email"])
    if request.method=="POST":    
        try:
            image_val=request.FILES["propic"]
        except:
            image_val=data.propic
        if request.POST["oldpswd"]:
            if check_password(request.POST["oldpswd"],data.password):
                data.name=request.POST["name"]
                data.password=make_password(request.POST["newpswd"])
                data.propic=image_val
                data.save()
                return render(request,"profile.html",{"data":data,"msg":"Profile Update Succesfully"})
            else:
                return render(request,"profile.html",{"data":data,"msg":"Old Passwrod not Match"})

        else:
            data.name=request.POST["name"]
            data.propic=image_val
            data.save()
            return render(request,"profile.html",{"data":data,"msg":"Profile Update Succesfully"})
    else:
        return render(request,"profile.html",{"data":data})
    
def show_products(request):
        all_product=Product.objects.all()
        return render(request,"shop-list.html",{"all_product":all_product})

def single_product(request,pk):
     one_product=Product.objects.get(id=pk)
     return render(request,"product-left-thumbnail.html",{"one_product":one_product})

def add_to_cart(request,pk):
    data=User.objects.get(email=request.session["email"])

    try:
        exists_data=Cart.objects.get(Q(prd_id=pk) & Q(buyer_id=data.id))
        exists_data.qty+=1
        exists_data.total= exists_data.qty*exists_data.prd_id.pro_price
        exists_data.save()
        return single_product(request,pk)
    except:
        prod=Product.objects.get(id=pk)
        Cart.objects.create(
            prd_id=prod,
            buyer_id=data,
            qty=1,
            total=Product.pro_price
        )
        return single_product(request,pk)
    

def show_cart(request):
    data=User.objects.get(email=request.session["email"])
    all_cart=Cart.objects.filter(buyer_id=data.id)
    return render(request,"cart.html",{"all_cart":all_cart})

def remove_cart(request,pk):
    one_cart=Cart.objects.get(id=pk)
    one_cart.delete()
    return show_cart(request)

def update_cart(request):
    if request.method=="POST":
        l1=request.POST.getlist("quantity")
        all_cart=Cart.objects.all()
        for i,j in zip(all_cart,l1):
            i.qty=j
            i.total=int(j)*i.prd_id.pro_price
            i.save()

        return show_cart(request)
    else:
        return show_cart(request)





    




    
# def otp_view(request):
#     # Generate and send the OTP to the user
#     send_otp_to_user()  # Replace with your OTP generation and sending logic

#     # Delay for a certain amount of time (e.g., 5 seconds)
#     time.sleep(5)

#     # Render the otp.html template
#     return render(request, 'otp.html')




