from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.statistics, name='statistics'),
    path('category_charts/', views.category_charts, name='category_charts'),
    path('groups_charts/', views.groups_charts, name='groups_charts'),
    path('shops_charts/', views.shops_charts, name='shops_charts'),
]