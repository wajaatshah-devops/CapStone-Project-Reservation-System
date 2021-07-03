from django.db import models
from fitnessClass.models import FitnessClass
from accounts.models import *

# Create your models here.
class Reservation(models.Model):
    classReserved = models.ForeignKey(FitnessClass, null=True, on_delete=models.CASCADE)
    customerReserving = models.ForeignKey(Account, null=True, on_delete=models.CASCADE)
    classDate = models.DateField(default=None)
    reservationStatus = models.CharField(max_length=20, default=None)
    reservationTimeStamp = models.DateTimeField(auto_now_add=True, blank=True)

    # Reservation Date = {self.reservationDate}, Reservation Time = {self.reservationTime}
    def __str__(self):
        return f'Class Reserved = {self.classReserved}, Customer Reserving {self.customerReserving}, Class Date = {self.classDate}'