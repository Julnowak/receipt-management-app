from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    # Home page
    path('', views.homepage, name='homepage'),
    path('contact/', views.contact, name='contact'),
    path('your_lists/', views.your_lists, name='your_lists'),
    path('single_list/<int:list_id>/', views.single_list, name='single_list'),
    path('details/<int:list_id>/', views.details, name='details'),
    path('details_redirected/<int:list_id>/', views.details_redirected, name='details_redirected'),
    path('<int:group_id>/single_list_redirected/<int:list_id>/', views.single_list_redirected, name='single_list_redirected'),
    path('del_shopping_lists/', views.del_shopping_lists, name='del_shopping_lists'),
    path('new_product/<int:list_id>/', views.new_product, name='new_product'),
    path('new_list/', views.new_list, name='new_list'),
    path('share_list/<int:list_id>/', views.share_list, name='share_list'),
    path('main_panel/', views.main_panel, name="main_panel"),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('edit_list/<int:list_id>/', views.edit_list, name='edit_list'),
    path('removed/<int:product_id>/', views.removed, name='removed'),
    path('removed_list/<int:list_id>/', views.list_removed, name='list_removed'),
    path('<int:list_id>/update_is_bought/', views.update_is_bought, name='update_is_bought'),
    path('<int:list_id>/current_number/', views.current_number, name='current_number'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)