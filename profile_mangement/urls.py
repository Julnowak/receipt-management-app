from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.profile_management_site, name='profile_management_site'),
    path('account_deletion/', views.account_deletion, name='account_deletion'),
    path('<int:member_id>/profile_showcase/', views.profile_showcase, name='profile_showcase'),
    path('deletion/', views.deletion, name="deletion"),
    path('change_visibility/', views.change_visibility, name="change_visibility"),
    path('change_email/', views.change_email, name="change_email"),
    path('change_image/', views.change_image, name="change_image"),
    path('change_description/', views.change_description, name="change_description"),
    path('change_name/', views.change_name, name="change_name"),
]