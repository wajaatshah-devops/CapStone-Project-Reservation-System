from datetime import date
from django.shortcuts import render, redirect
from datetime import datetime, date
from accounts.models import *
from django.contrib.auth.decorators import login_required
from accounts.forms import *

@login_required(login_url="accounts:login")
def staff_help_view(request):
    if request.user.is_staff == False:
        return render(request, 'helpVids/help.html')
    return render(request, 'helpVids/staffHelp.html')

# Anyone should be able to access help videos no login required
def help_view(request):
    return render(request, 'helpVids/help.html')