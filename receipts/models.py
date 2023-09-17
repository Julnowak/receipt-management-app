from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Receipt(models.Model):
    receipt_name = models.CharField(max_length=200)
    receipt_img = models.ImageField(upload_to='images/')
    date_added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.receipt_name
