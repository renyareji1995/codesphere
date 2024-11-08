from django.shortcuts import render,redirect,get_object_or_404

from django.urls import reverse_lazy

from django.views.generic import View,FormView,CreateView,TemplateView

from store.forms import SignUpForm,SignInForm,UserProfileForm,ProjectForm

from django.db.models import Sum

from store.models import Project,WishListItem,Order

from django.contrib.auth import authenticate,login,logout

from django.views.decorators.csrf import csrf_exempt

from django.utils.decorators import method_decorator

from django.contrib import messages

from django.contrib import messages

from django.core.mail import send_mail

from store.decorators import signin_required

from django.views.decorators.cache import never_cache



def send_email():
    send_mail(
    "codehub project download",
    "You have completed purchase",
    "renyareji2013@gmail.com",
    ["renyareji9539@gmail.com"],
    fail_silently=False,
)
decs=[signin_required,never_cache]


class SignUpView(CreateView):

    template_name="register.html"

    form_class=SignUpForm

    success_url=reverse_lazy("signin")

    # def get(self,request,*args,**kwargs):

    #     form_instance=self.form_class()

    #     return render(request,self.template_name,{"form":form_instance})
    

    # def post(self,request,*args,**kwargs):

    #     form_instance=self.form_class(request.POST)

    #     if form_instance.is_valid():

    #         form_instance.save()

    #         print("account created")

    #         messages.success(request,"account created")

    #         return redirect("signup")
        
    #     else:

    #         messages.error(request,"failed to create account")

    #         return render(request,self.template_name,{"form":form_instance})
        

class SignInView(FormView):

    template_name="login.html"

    form_class=SignInForm


    def post(self,request,*args,**kwargs):

        form_instance=self.form_class(request.POST)

        if form_instance.is_valid():

            uname=form_instance.cleaned_data.get("username")

            pwd=form_instance.cleaned_data.get("password")

            user_object=authenticate(username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect("index")
            
        return render(request,self.template_name,{"form":form_instance})


@method_decorator(decs,name="dispatch")
class IndexView(View):

    template_name="index.html"

    def get(self,request,*args,**kwargs):

        qs=Project.objects.all().exclude(developer=request.user)

        return render(request,self.template_name,{"data":qs})


class LogoutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("signin")
    
#function based view
# def logout_view(request,*args,**kwargs):

#     logout(request)

#     return redirect("signin")


@method_decorator(decs,name="dispatch")
class UserProfileEditView(View):

    template_name="profile_edit.html"

    form_class=UserProfileForm

    def get(self,request,*args,**kwargs):

        user_profile_instance=request.user.profile

        form_instance=UserProfileForm(instance=user_profile_instance)

        return render(request,self.template_name,{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        user_profile_instance=request.user.profile

        form_instance=UserProfileForm(request.POST,instance=user_profile_instance,files=request.FILES)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("index")
        
        return render(request,self.template_name,{"form":form_instance})
    

@method_decorator(decs,name="dispatch")
class ProjectCreateView(View):

    template_name="project_add.html"

    form_class=ProjectForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class

        return render(request,self.template_name,{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        form_instance=self.form_class(request.POST,files=request.FILES)

        if form_instance.is_valid():

            form_instance.instance.developer=request.user

            form_instance.save()

            return redirect("index")
        
        return render(request,self.template_name,{"form":form_instance})
    
@method_decorator(decs,name="dispatch")
class MyProjectListView(View):

    template_name="my_projects.html"

    def get(self,request,*args,**kwargs):

        qs=Project.objects.filter(developer=request.user)

        return render(request,self.template_name,{"data":qs})

@method_decorator(decs,name="dispatch")
class ProjectUpdateView(View):

    template_name="project_update.html"

    form_class=ProjectForm

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        project_object=Project.objects.get(id=id)

        form_instance=self.form_class(instance=project_object)

        return render(request,self.template_name,{"form":form_instance})
    

    def post(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        project_object=Project.objects.get(id=id)

        form_instance=self.form_class(request.POST,instance=project_object,files=request.FILES)

        if form_instance.is_valid():

            form_instance.save()

            return redirect("my-works")
        
        return render(request,self.template_name,{"form":form_instance})
    
@method_decorator(decs,name="dispatch")
class ProjectDetailView(View):

    template_name="project_detail.html"

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        qs=Project.objects.get(id=id)

        return render(request,self.template_name,{"data":qs})
    

@method_decorator(decs,name="dispatch")
class AddToWishlistItemView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        project_object=get_object_or_404(Project,id=id)

        try:

            request.user.basket.basket_item.create(project_object=project_object)

            messages.success(request,"item has benn added to wishlist")
        
        except Exception as e:

            messages.error(request,"failed to add item ")


        return redirect("index")
    
@method_decorator(decs,name="dispatch")
class MyWishListItemsView(View):

    template_name="my_wishlist.html"

    def get(self,request,*args,**kwargs):

        
            qs=request.user.basket.basket_item.filter(is_order_placed=False)

            total=qs.values("project_object").aggregate(total=Sum("project_object__price")).get("total")

            print("total",total)
            
            return render(request,self.template_name,{"data":qs,"total":total})
    
@method_decorator(decs,name="dispatch")
class WishListItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        WishListItem.objects.get(id=id).delete()

        return redirect("my-wishlist")
    

import razorpay   
@method_decorator(decs,name="dispatch")
class CheckOutView(View):

    template_name="checkout.html"

    def get(self,request,*args,**kwargs):

        #step 1 razorpay authentication
        KEY_ID="rzp_test_5I5g3qdA7jcHg9"

        KEY_SECRET="n5XBsxBFUT2iQ2a9bfRXtlUP"

        #authenticate
        client=razorpay.Client(auth=(KEY_ID,KEY_SECRET))

        #order_create in razorpay
        amount=request.user.basket.basket_item.filter(is_order_placed=False).values("project_object").aggregate(total=Sum("project_object__price")).get("total")

        data = { "amount": amount*100, "currency": "INR", "receipt": "order_rcptid_code_hub" }

        payment = client.order.create(data=data)

        print(payment)

        """
        {'amount': 500000, 'amount_due': 500000, 'amount_paid': 0, 'attempts': 0,
          'created_at': 1730836540, 'currency': 'INR', 'entity': 'order',
            'id': 'order_PHkL8f0NLQXIYk', 'notes': [], 'offer_id': None, 
        'receipt': 'order_rcptid_code_hub', 'status': 'created'}
        """

        order_id=payment.get("id")

        #create orderin database

        order_object=Order.objects.create(order_id=order_id,customer=request.user)

        wishlist_items=request.user.basket.basket_item.filter(is_order_placed=False)

        for wi in wishlist_items:

            order_object.wishlist_item_objects.add(wi)

            wi.is_order_placed=True

            wi.save()

        return render(request,self.template_name,{"key_id":KEY_ID,"amount":amount,"order_id":order_id})
    

@method_decorator(decs,name="dispatch")
@method_decorator(csrf_exempt,name="dispatch")
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST)
        # <QueryDict: {'razorpay_payment_id': ['pay_PIoA2HK4yjRDWX'], 
        #              'razorpay_order_id': ['order_PIo9dMcE3MBDWo'],
        #               'razorpay_signature': ['fb33455d97961f7fe1654a0db53f2c7df6958dd3f100c3d1ddb2f451dcdd90de']}>
        # verify
        # error-failed
        # success-completed

        KEY_ID="rzp_test_5I5g3qdA7jcHg9"

        KEY_SECRET="n5XBsxBFUT2iQ2a9bfRXtlUP"

        #to verify the payment is success or failed
        #by generating signature on server
        client = razorpay.Client(auth=(KEY_ID,KEY_SECRET))

        try:
            client.utility.verify_payment_signature(request.POST)

            order_id=request.POST.get("razorpay_order_id")

            Order.objects.filter(order_id=order_id).update(is_paid=True)
            send_email()

            print("success")

        except:

            print("failed")

        return redirect("orders")


#MyOrdersView
@method_decorator(decs,name="dispatch")
class MyOrdersView(View):

    template_name="myorders.html"

    def get(self,request,*args,**kwargs):

        qs=Order.objects.filter(customer=request.user)

        return render(request,self.template_name,{"data":qs})






        










    







