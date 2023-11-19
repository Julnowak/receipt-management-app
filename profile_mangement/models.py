from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.


text = """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" fill="currentColor" class="bi bi-person-circle" viewBox="0 0 16 16"><path d="M11 6a3 3 0 1 1-6 0 3 3 0 0 1 6 0z"/><path fill-rule="evenodd" d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm8-7a7 7 0 0 0-5.468 11.37C3.242 11.226 4.805 10 8 10s4.757 1.225 5.468 2.37A7 7 0 0 0 8 1z"/></svg>"""


class Icon(models.Model):
    icon_name = models.CharField(max_length=200)
    icon_code = models.CharField(max_length=1500, blank=True, null=True, default=text)

    def __str__(self):
        return self.icon_name


class ProfileInfo(models.Model):
    profile_image = models.ForeignKey(Icon,on_delete=models.SET_NULL, blank=True, null=True)
    profile_image_color = models.CharField(max_length=7, default="#000000")
    profile_image_background_color = models.CharField(max_length=7, default="#FFFFFF")
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    email = models.EmailField()
    date_of_birth = models.DateField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    messages_by_groups = models.BooleanField(default=True)
    messages_by_users = models.BooleanField(default=True)
    blocked_users = models.ManyToManyField(User, related_name="blocked_users", blank=True)
    how_many_receipts = models.IntegerField(default=0)
    how_many_guarantees = models.IntegerField(default=0)
    how_many_expenses = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username