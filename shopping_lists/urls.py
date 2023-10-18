from django.urls import path, include
from . import views

urlpatterns = [

    # Home page
    path('', views.homepage, name='homepage'),
    path('contact/', views.contact, name='contact'),
    path('your_lists/', views.your_lists, name='your_lists'),
    path('your_lists/<int:list_id>/', views.single_list, name='single_list'),
    path('add_shopping_list/', views.add_shopping_list, name='add_shopping_list'),
    path('del_shopping_lists/', views.del_shopping_lists, name='del_shopping_lists'),
    path('edit_shopping_lists/<int:list_id>/', views.edit_shopping_lists, name='edit_shopping_lists'),
    path('new_product/<int:list_id>/', views.new_product, name='new_product'),
    path('share_list/<int:list_id>/', views.share_list, name='share_list'),
    path('main_panel/', views.main_panel, name="main_panel"),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('removed/<int:product_id>/', views.removed, name='removed'),
    path('removed_list/<int:list_id>/', views.list_removed, name='list_removed'),
    path('share_list/', views.share_list, name='share_list'),
]