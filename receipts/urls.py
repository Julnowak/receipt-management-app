from django.urls import path, include
from . import views

app_name = 'receipts'
urlpatterns = [
    path('', views.your_receipts, name='your_receipts'),


]