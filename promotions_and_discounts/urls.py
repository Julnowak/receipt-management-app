from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'promotions_and_discounts'
urlpatterns = [
    path('', views.shop_selection, name='shop_selection'),
    path('<slug:shop_slug>', views.shop_site, name='shop_site'),
]