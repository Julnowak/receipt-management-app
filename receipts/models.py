from django.db import models
from django.contrib.auth.models import User
from categories.models import BaseCategories
from groups.models import CommonGroups
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

TIME_STAMP_CHOICES = (
    ("MINUT", "Minut"),
    ("GODZIN", "Godzin"),
    ("TYGODNI", "Tygodni"),
    ("MIESIĘCY", "Miesięcy"),
    ("LAT", "Lat"),
)


class ListProduct(models.Model):
    product_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=400, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'list products'

    def __str__(self):
        return self.product_name


class Receipt(models.Model):
    receipt_name = models.CharField(max_length=200)
    receipt_img = models.ImageField(upload_to='images/')
    date_added = models.DateField(auto_now_add=True)
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=20, validators=[MinValueValidator(0.00)], blank=True, null=True)
    receipt_info = models.TextField(default="", null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CommonGroups, on_delete=models.CASCADE, blank=True, null=True)
    products = models.ManyToManyField(ListProduct, blank=True, null=True)

    def __str__(self):
        return self.receipt_name


class Expense(models.Model):
    expense_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    is_recurrent = models.BooleanField(default=False)
    amount = models.DecimalField(default=0.00, decimal_places=2, max_digits=20, validators=[MinValueValidator(0.00)])
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(BaseCategories, on_delete=models.CASCADE)
    group = models.ForeignKey(CommonGroups, on_delete=models.CASCADE, blank=True, null=True)
    number = models.PositiveIntegerField(blank=True, null=True)
    time_stamp = models.CharField(max_length=12, choices=TIME_STAMP_CHOICES,default="MIESIĘCY", blank=True, null=True)

    def __str__(self):
        return self.expense_name


class Guarantee(models.Model):
    guarantee_name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    regards = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.guarantee_name