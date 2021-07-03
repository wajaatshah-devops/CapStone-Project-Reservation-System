from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, firstName, lastName, street, city, state, zipcode, phoneNumber, password):
        if not email:
            raise ValueError('Email address is required')
        if not username:
            raise ValueError('Username is required')
        if not firstName:
            raise ValueError('First name is required')
        if not lastName:
            raise ValueError('Last name is required')
        if not street:
            raise ValueError('Street address is required')
        if not city:
            raise ValueError('City is required')
        if not state:
            raise ValueError('State is required')
        if not zipcode:
            raise ValueError('Zipcode is required')
        if not phoneNumber:
            raise ValueError('Phone number is required')
        if not password:
            raise ValueError('Password is required')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            password = password,
            firstName = firstName,
            lastName = lastName,
            street = street,
            city = city,
            state = state,
            zipcode = zipcode,
            phoneNumber = phoneNumber,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, firstName, lastName, street, city, state, zipcode, phoneNumber, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            firstName = firstName,
            lastName = lastName,
            street = street,
            city = city,
            state = state,
            zipcode = zipcode,
            phoneNumber = phoneNumber
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now = True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    firstName = models.CharField(max_length=20, null=True)
    lastName = models.CharField(max_length=20, null=True)
    street = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=20, null=True)
    zipcode = models.CharField(max_length=20, null=True)
    phoneNumber = models.CharField(max_length=20, null=True)

    verificationChoices = [
        ('Annual', 'Annual Pass Holder'),
        ('Resident', 'Town of Leesburg Resident'),
        ('Neither', 'Neither'),
        ('UnVerified', 'UnVerified')
    ]
    verified = models.CharField(max_length=20, default="UnVerified", choices=verificationChoices)    

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'firstName', 'lastName', 'street', 'city', 'state', 'zipcode', 'phoneNumber']

    objects = MyAccountManager()

    def __str__ (self):
        return f'{self.firstName} - {self.lastName} - {self.email}'

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True