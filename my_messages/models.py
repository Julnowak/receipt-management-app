from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Message(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    slug = models.SlugField(default="")
    date_created = models.DateField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")

    def __str__(self):
        return self.title
