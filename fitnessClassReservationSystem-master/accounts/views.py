from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from accounts.forms import UserForm
from django.contrib.auth import login, logout
from . models import *

def signup_view(request):
    statement = ''
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email').lower().strip()
            username = form.cleaned_data.get('username').lower().strip()
            firstName = form.cleaned_data.get('firstName').lower().strip()
            lastName = form.cleaned_data.get('lastName').lower().strip()
            street = form.cleaned_data.get('street').lower().strip()
            city = form.cleaned_data.get('city').lower().strip()
            state = form.cleaned_data.get('state').lower().strip()           
            zipcode = form.cleaned_data.get('zipcode').lower().strip()
            phoneNumber = request.POST.get('phoneNumber').lower().strip()
            password = form.cleaned_data.get('password1').strip()
            try:
                user = Account.objects.create_user(email, username, firstName, lastName, street, city, state, zipcode, phoneNumber, password)
            except ValueError as e:
                errorMessage = e
                return render(request, 'accounts/signup.html', {'form': form, 'statement':errorMessage})
            if request.user.is_staff:
                return redirect('fitnessClass:schedule')
            login(request, user)
            return redirect('fitnessClass:schedule')
        else:
            statement = ""
    else:
        form = UserForm()
    return render(request, 'accounts/signup.html', { 'form': form, 'statement':statement })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
               return redirect('fitnessClass:schedule')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', { 'form': form })

def logout_view(request):
    if request.method == 'GET':
        logout(request)
        form = AuthenticationForm
        return render(request, 'accounts/login.html', {'form':form})