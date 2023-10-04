from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.profile_management_site, name='profile_management_site'),
]