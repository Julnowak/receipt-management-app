from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.profile_management_site, name='profile_management_site'),
    path('account_deletion/', views.account_deletion, name='account_deletion'),
    path('account_management/', views.account_management, name='account_management'),
    path('<int:member_id>/profile_showcase/', views.profile_showcase, name='profile_showcase')
]