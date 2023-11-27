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
    path('<int:group_id>/group_receipts_and_expenses/', views.group_receipts_and_expenses, name='group_receipts_and_expenses'),
    path('search_group/', views.search_group, name='search_group'),
    path('delete_group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('group_deletion/<int:group_id>/', views.group_deletion, name='group_deletion'),
    path('<int:group_id>/password_check/', views.password_check, name='password_check'),
    path('<int:group_id>/change_limit/', views.change_limit, name='change_limit'),
    path('<int:group_id>/change_adding_possibility/', views.change_adding_possibility, name='change_adding_possibility'),
    path('<int:group_id>/not_member_of_group/', views.not_member_of_group, name='not_member_of_group'),
    path('<int:group_id>/change_invite_possibility/', views.change_invite_possibility, name='change_invite_possibility'),
    path('<int:group_id>/remove_member/<int:member_id>/', views.remove_member, name='remove_member'),
    path('<int:group_id>/del_from_group_expenses/<int:expense_id>/', views.del_from_group_expenses, name='del_from_group_expenses'),
    path('<int:group_id>/del_from_group_receipts/<int:receipt_id>/', views.del_from_group_receipts, name='del_from_group_receipts'),
    path('<int:group_id>/profile_not_public/', views.profile_not_public, name='profile_not_public'),
]