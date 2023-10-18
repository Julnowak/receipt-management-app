from django.db import models
from django.contrib.auth.models import User
from groups.models import CommonGroups

# Create your models here.


class Message(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    slug = models.SlugField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    new = models.BooleanField(default=True)
    message_type = models.CharField(max_length=200, default="normal")
    group = models.ForeignKey(CommonGroups, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if len(self.title) < 20:
            return self.title
        else:
            return self.title[:20] + "..."
