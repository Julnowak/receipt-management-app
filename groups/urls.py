from django.urls import path, include
from . import views

app_name = 'groups'
urlpatterns = [
    path('', views.groups, name='groups'),
    path('<int:group_id>/', views.group_site, name='group_site'),
    path('<int:group_id>/invite/', views.invite_page, name='invite_page'),
    path('<int:group_id>/leave_group/', views.leaving_group_page, name='leaving_group_page'),
    path('add_group/', views.add_group, name='add_group'),
    path('<int:group_id>/invite/search/', views.search, name='search'),
    path('<int:group_id>/leave_group/left/', views.left_group, name='left_group'),
    path('<int:group_id>/manage_group/', views.manage_group, name='manage_group'),
    path('search_group/', views.search_group, name='search_group'),
]