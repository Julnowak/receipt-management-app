from django.urls import path, include
from . import views

urlpatterns = [

    # Home page
    path('', views.homepage, name='homepage'),
    path('your_lists/', views.your_lists, name='your_lists'),
    path('your_lists/<int:list_id>/', views.single_list, name='single_list'),
    path('new_list/', views.new_list, name='new_list'),
    path('new_product/<int:list_id>/', views.new_product, name='new_product'),
    path('main_panel/', views.main_panel, name="main_panel"),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('removed/<int:product_id>/', views.removed, name='removed'),
    path('removed_list/<int:list_id>/', views.list_removed, name='list_removed'),
]