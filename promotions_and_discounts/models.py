from django.db import models
from django.utils.text import slugify

# Create your models here.


class Shop(models.Model):
    shop_name = models.CharField(max_length=200)
    image = models.ImageField(blank=True, null=True)
    link = models.CharField(max_length=2000)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.shop_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.shop_name)
        super(Shop, self).save(*args, **kwargs)
