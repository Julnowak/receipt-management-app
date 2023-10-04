from django.urls import path, include
from . import views

app_name = 'receipts'
urlpatterns = [
    path('', views.your_receipts, name='your_receipts'),
    path('new_receipt/', views.new_receipt, name='new_receipt'),
    path('costs_by_hand/', views.costs_by_hand, name='costs_by_hand'),
]