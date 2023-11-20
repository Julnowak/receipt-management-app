from django.urls import path, include
from . import views

app_name = 'categories'
urlpatterns = [
    path('', views.categories, name='categories'),
    path('new_category/', views.new_category, name='new_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('<int:category_id>/', views.subcategories, name='subcategories'),
    path('<int:category_id>/new_subcategory/', views.new_subcategory, name='new_subcategory'),
    path('<int:category_id>/edit_subcategory/', views.edit_subcategory, name='edit_subcategory'),
    path('products_in_subcategory/<int:subcategory_id>', views.products_in_subcategory, name='products_in_subcategory')
]