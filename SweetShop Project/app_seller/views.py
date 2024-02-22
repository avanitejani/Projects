
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
import random
from .models import *
from django.contrib.auth.hashers import make_password,check_password


# Create your views here.
def index(request):
    return render(request,"seller_index.html")

def seller_register(request):
    if request.method=="POST":
        global temp
        temp={
            "name":request.POST["name"],
            "email":request.POST["email"],
            "password":request.POST["pswd"]# pswd =seller_sing-up.html se fild name hai

        }
        global otp
        otp=random.randint(100000,999999)
        subject = 'OTP Verification'
        message = f'Your OTP is. {otp} valid for 5 mintute only'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.POST["email"],  ]
        send_mail( subject, message, email_from, recipient_list )
        return render(request,"seller_otp.html")
    else:
        return render(request,"seller_sign-up.html")

def otp(request):   
    if request.method=="POST":
        if otp==int(request.POST["otp"]):
            Seller_user.objects.create(
                name=temp["name"],
                email=temp["email"],
                password=make_password(temp["password"])

            )
            return render(request,"seller_sign-up.html",{"msg":"registation successfull"})
        else:
            return render(request,"seller_sign-up.html",{"msg":"otp not matched"})


    else: 
        return render(request,"seller_sign-up.html")
    
def seller_login(request):
    if request.method=="POST":
        try:
            User_data = Seller_user.objects.get(email = request.POST["email"])
            check_password(request.POST["Password"],User_data.password)
            request.session["email"]=request.POST["email"]
            return render(request,"seller_shop-list.html")
            
                # return render(request,"seller_login.html",{"msg":"Password Not Match"})
        except:
            return render(request,"seller_login.html",{"msg":"seller not Exist"})
    else:
        return render(request,"seller_login.html")
    
def seller_logout(request):
    del request.session["email"]
    return render(request,"seller_login.html",{"msg":"Logout Successfully"})

def add_product(request):
    seller_data=Seller_user.objects.get(email=request.session["email"])
    if request.method=="POST":
        Product.objects.create(
            pro_name=request.POST["pname"],
            pro_price=request.POST["pro_price"],
            pro_qty=request.POST["pro_qty"],
            pro_image=request.FILES["p_image"],
            pro_desc=request.POST["pro_desc"],
            seller_id=seller_data
        )
        return render(request,"add_product.html",{"seller_data":seller_data,"msg":"Product added Successfull"})

    else:
        return render(request,"add_product.html",{"seller_data":seller_data})
    

def seller_profile(request):
    data=Seller_user.objects.get(email=request.session["email"])
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
                return render(request,"seller_profile.html",{"data":data,"msg":"Profile Update Succesfully"})
            else:
                return render(request,"seller_profile.html",{"data":data,"msg":"Old Passwrod not Match"})

        else:
            data.name=request.POST["name"]
            data.propic=image_val
            data.save()
            return render(request,"seller_profile.html",{"data":data,"msg":"Profile Update Succesfully"})
    else:
        return render(request,"seller_profile.html",{"data":data})
    
# def seller_view_product(request):
#     seller_data=Seller_user.object.get(email=request.session["email"])
#     my_product=Product.object.objects.filter(id=seller_data)
#     return render(request,"my_product.html",{"my_product",my_product})
    

def seller_show_products(request):
    all_product=Product.objects.all()
    return render(request,"seller_shop-list.html",{"all_product":all_product})

# def singal(request):
#     url = "https://api.countrystatecity.in/v1/countries/BD"

#     headers={
#         "X-CSCAPI-KEY": "UXF20HQ2WJBMT1Y5Q05MQzVhNE1sT3VJSk02Y3BaNz1RNHRVMHRjZA=="
#     }

#     mydata = requests.request("GEt")




    
# def otp_view(request):
#     # Generate and send the OTP to the user
#     send_otp_to_user()  # Replace with your OTP generation and sending logic

#     # Delay for a certain amount of time (e.g., 5 seconds)
#     time.sleep(5)

#     # Render the otp.html template
#     return render(request, 'otp.html')




