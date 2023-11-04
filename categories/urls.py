from django.urls import path, include
from . import views

app_name = 'categories'
urlpatterns = [
    path('', views.categories, name='categories'),
    path('new_category/', views.new_category, name='new_category'),
    path('edit_category/<slug:category_slug>/', views.edit_category, name='edit_category'),
    path('<slug:category_slug>/', views.subcategories, name='subcategories'),
    path('<slug:category_slug>/new_subcategory/', views.new_subcategory, name='new_subcategory'),
    path('<slug:category_slug>/edit_subcategory/', views.edit_subcategory, name='edit_subcategory'),
]