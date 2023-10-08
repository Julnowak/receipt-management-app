from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.profile_management_site, name='profile_management_site'),
    path('account_deletion/', views.account_deletion, name='account_deletion')
]