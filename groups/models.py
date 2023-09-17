from django.db import models
from django.contrib.auth.models import User
import random
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


def random_passwd_generator():
    s = r' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    numbers = list(range(len(s)))
    pswd = ''
    for _ in range(20):
        pswd += s[random.choice(numbers)]
    return pswd


class CommonGroups(models.Model):
    group_name = models.CharField(max_length=200)
    slug = models.SlugField(default="")
    date_created = models.DateField(auto_now_add=True)
    number_of_members = models.IntegerField(validators=[MaxValueValidator(50), MinValueValidator(1)], default=1)
    max_number_of_members = models.IntegerField(default=5)
    password = models.CharField(max_length=200, default=random_passwd_generator())
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    members = models.ManyToManyField(User, related_name='member')

    def __str__(self):
        return self.group_name

