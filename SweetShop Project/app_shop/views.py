from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
import random
from .models import *
from app_seller.models import *
from django.db.models import Q
from django.contrib.auth.hashers import make_password,check_password

from django.shortcuts import render
import razorpay
import requests

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest


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
            total=prod.pro_price
        )
        return single_product(request,pk)
    
def checkout(request):
    # data=User.objects.get(email=request.session["email"])
    # all_cart=Cart.objects.filter(buyer_id=data.id)
    # final_total=0
    # for i in all_cart:
    #     final_total+=i.total
    return render(request,"checkout.html")

     
    

def show_cart(request):
    data=User.objects.get(email=request.session["email"])
    all_cart=Cart.objects.filter(buyer_id=data.id)
    sub_total=0
    for i in all_cart:
        sub_total+=i.total
    final_total=sub_total+8
    return render(request,"cart.html",{"all_cart":all_cart,"sub_total":sub_total,"final_total":final_total})


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
    
def search(request):
    if request.method=="POST":
         query = request.POST['ser']
         all_product=Product.objects.filter(Q(pro_name__icontains=query)|Q(pro_desc__icontains=query))
         return render(request,"shop-list.html",{"all_product":all_product})
    else:
         return show_products(request)
    




def countries(request):
    url = "https://api.countrystatecity.in/v1/countries"

    headers = {
    "X-CSCAPI-KEY": "UXF2OHQ2WjBMT1Y5Q05MQzVhNE1sT3VJSk02Y3BaNzlRNHRVMHRjZA=="
    }

    mydata =  requests.request("GET", url, headers=headers)
    return render(request,'country.html',{"mydata":mydata.json()})


def single(request):
    url = "https://api.countrystatecity.in/v1/countries/BD"

    headers = {
    "X-CSCAPI-KEY": "UXF2OHQ2WjBMT1Y5Q05MQzVhNE1sT3VJSk02Y3BaNzlRNHRVMHRjZA=="
    }

    mydata = requests.request("GET", url, headers=headers)
    return render(request,'one_country.html',{"mydata":mydata.json()})

def con_ser(request):
    if request.method=="POST":
          item=request.POST["con"]
          url = "https://api.countrystatecity.in/v1/countries/BD"
          headers = {
          "X-CSCAPI-KEY": "UXF2OHQ2WjBMT1Y5Q05MQzVhNE1sT3VJSk02Y3BaNzlRNHRVMHRjZA=="
          }

          all_country = requests.request("GET", url, headers=headers).json()
          for i in all_country:
                if i["name"]==item.title():
                    my_id=i["iso2"] 
          try: 
                url = "https://api.countrystatecity.in/v1/countries/{my_id}"
                headers = {
                "X-CSCAPI-KEY": "UXF2OHQ2WjBMT1Y5Q05MQzVhNE1sT3VJSk02Y3BaNzlRNHRVMHRjZA=="
                }
                mydata = requests.request("GET", url, headers=headers).json()
                return render(request,'concer.html',{"mydata":mydata})

          except:
                return render(request,'concer.html',{"msg":"Not found"})
    else:
          return render(request,"concer.html")

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):

	# only accept POST request.
	if request.method == "POST":
		try:
		
			# get the required parameters from post request.
			payment_id = request.POST.get('razorpay_payment_id', '')
			razorpay_order_id = request.POST.get('razorpay_order_id', '')
			signature = request.POST.get('razorpay_signature', '')
			params_dict = {
				'razorpay_order_id': razorpay_order_id,
				'razorpay_payment_id': payment_id,
				'razorpay_signature': signature
			}

			# verify the payment signature.
			result = razorpay_client.utility.verify_payment_signature(
				params_dict)
			if result is not None:
				amount = 20000 # Rs. 200
				try:

					# capture the payemt
					razorpay_client.payment.capture(payment_id, amount)

					# render success page on successful caputre of payment
					return render(request, 'paymentsuccess.html')
				except:

					# if there is an error while capturing payment.
					return render(request, 'paymentfail.html')
			else:

				# if signature verification fails.
				return render(request, 'paymentfail.html')
		except:

			# if we don't find the required parameters in POST data
			return HttpResponseBadRequest()
	else:
	# if other than POST request is made.
		return HttpResponseBadRequest()







    




    
# def otp_view(request):
#     # Generate and send the OTP to the user
#     send_otp_to_user()  # Replace with your OTP generation and sending logic

#     # Delay for a certain amount of time (e.g., 5 seconds)
#     time.sleep(5)

#     # Render the otp.html template
#     return render(request, 'otp.html')




