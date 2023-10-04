from django.db import models
from django.contrib.auth.models import User
from categories.models import BaseCategories
from groups.models import CommonGroups

# Create your models here.


class Receipt(models.Model):
    receipt_name = models.CharField(max_length=200)
    receipt_img = models.ImageField(upload_to='images/')
    date_added = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.receipt_name


class Expense(models.Model):
    expense_name = models.CharField(max_length=200)
    date_added = models.DateField(auto_now_add=True)
    is_recurrent = models.BooleanField(default=False)
    amount = models.FloatField(default=0.00)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BaseCategories, on_delete=models.CASCADE)
    group = models.ForeignKey(CommonGroups, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.expense_name