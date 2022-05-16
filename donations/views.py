from datetime import datetime
from django.shortcuts import render, redirect

from django.views.generic import View

from django.core.paginator import Paginator

from donations.models import Donation, Institution, Category
from django.contrib.auth.models import User

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    #PermissionRequiredMixin,
    #UserPassesTestMixin,
    #PermissionDenied
)

class LandingPage(View):
    def get(self, request):
        donations = Donation.objects.all()
        total_quantity = 0
        total_institutions = 0
        for donation in donations:
            total_quantity += donation.quantity
            total_institutions += 1

        institutions = Institution.objects.all()
        #p = Paginator(institutions, 5) 
        #page = p.page(request.GET.get('page', 1))
        
        return render(request, 'index.html', { "tquantity": total_quantity,
                                                "tinstitutions": total_institutions,
                                                "institutions": institutions
                                              })


class AddDonation(LoginRequiredMixin, View):
    login_url = 'donations:login'
    #redirect_field_name = 'redirect_to'
    
    def get(self, request):
        categories = Category.objects.all()
        institutions = Institution.objects.all()
        return render(request, 'form.html', {"categories":categories,
                                            "institutions":institutions})

    def post(self, request):
        checked_categories = request.POST.getlist('categories') # list of Category id
        bags_quantity = int(request.POST.get('bags')) # no of bags quoted to donate
        organization_to_support = Institution.objects.get(id=int(request.POST.get('organization'))) # Institution id from HTML form
        
        address_street = request.POST.get('address')
        address_city = request.POST.get('city')
        address_postcode = request.POST.get('postcode')
        address_phone = request.POST.get('phone')
        
        send_date = request.POST.get('data')
        send_time = request.POST.get('time')
        send_remarks = request.POST.get('more_info')

        current_user = User.objects.get(id=request.user.id)

        """print(f"categories: {checked_categories}, bags: {bags_quantity}, \
                organization: {organization_to_support}, \
                address: {address_street}, {address_city}, {address_postcode}, {address_phone}, \
                send date: {send_date}, time: {send_time} \
                remarks: {send_remarks}")"""

        current_donation = Donation.objects.create(quantity=bags_quantity, institution=organization_to_support, \
        address=address_street, phone_number=address_phone, city=address_city, zip_code=address_postcode, \
        pick_up_date=send_date, pick_up_time=send_time, pick_up_comment=send_remarks, user=current_user)
        
        current_donation.save()

        for category in checked_categories:
            cat = Category.objects.get(id=int(category))
            current_donation.categories.add(cat)

        return render(request, 'form-confirmation.html')


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        email = request.POST.get('email')
        password_h = request.POST.get('password') 

        user = authenticate(request, username=email, password=password_h)
        if user:
            login(request, user)  #succesful authentication
            return redirect("donations:home")
        else: #user = none
            return redirect("donations:login")  #failed authentication

@login_required
def Logout(request):
    logout(request)
    return redirect("donations:home")


class Register(View):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        try:
            first_name=request.POST.get('name')
            last_name=request.POST.get('surname')
            email = request.POST.get('email')
            username = email
            pass1 = request.POST.get('password') 
            pass2 = request.POST.get('password2')
            if pass1 == pass2 and len(pass1)>5:
                password_hashed = make_password(request.POST.get('password'))
            
            User.objects.create(password=password_hashed, username=username, last_name=last_name, email=email, first_name=first_name)
            
            return redirect("donations:login")
        except:
            return render(request, 'register.html')


class UserView(LoginRequiredMixin, View):
    login_url = 'donations:login'

    def get(self, request):
        current_user = User.objects.get(username=request.user.username)
        donations = Donation.objects.filter(user=current_user.id)
        sum_of_all_bags = 0
        for donation in donations:
            sum_of_all_bags += donation.quantity

        today = datetime.now().date()
        
        return render(request, 'profil.html', { "current_user":current_user,
                                                "donations":donations,
                                                "sum_of_all_bags":sum_of_all_bags,
                                                "today":today
                                                })
