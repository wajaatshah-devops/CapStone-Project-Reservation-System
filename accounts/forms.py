from django.contrib.auth.forms import UserCreationForm
from django.forms.models import ModelForm
from .import models
from django.utils.translation import ugettext_lazy as _

class UserForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = models.Account
        fields = [ 'username', 'password1', 'password2', 'firstName', 'lastName', 'street', 'city', 'state', 'zipcode', 'email']
        labels = {
            'username': _('User Name'),
            'firstName' : _('First Name'),
            'lastName': _('Last Name'),
            'street': _('Street Address'),
            'city': _('City'),
            'state': _('State'),
            'zipcode': _('Zipcode'),
            'email': _('Email'),
        }

class staffCustomerForm(ModelForm):
    class Meta(ModelForm):
        model = models.Account
        fields = ['firstName', 'lastName', 'email']
        labels = {
            'firstName': _('First Name'),
            'lastName' : _('Last Name'),
            'email': _('Email')
        }