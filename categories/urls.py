from django.urls import path, include
from . import views

app_name = 'categories'
urlpatterns = [
    path('', views.categories, name='categories'),
    path('new_category/', views.new_category, name='new_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('<int:category_id>/', views.subcategories, name='subcategories'),
    path('<int:category_id>/delete_category/', views.delete_category, name='delete_category'),
    path('<int:subcategory_id>/delete_subcategory/', views.delete_subcategory, name='delete_subcategory'),
    path('<int:category_id>/new_subcategory/', views.new_subcategory, name='new_subcategory'),
    path('<int:subcategory_id>/edit_subcategory/', views.edit_subcategory, name='edit_subcategory'),
    path('<int:product_id>/edit_product/', views.edit_product, name='edit_product'),
    path('<int:subcategory_id>/new_product/', views.new_product, name='new_product'),
    path('<int:product_id>/delete_product/', views.delete_product, name='delete_product'),
    path('products_in_subcategory/<int:subcategory_id>', views.products_in_subcategory, name='products_in_subcategory')
]