from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'receipts'
urlpatterns = [
    path('', views.your_receipts, name='your_receipts'),
    path('guarantees/', views.guarantees, name='guarantees'),
    path('new_receipt/', views.new_receipt, name='new_receipt'),
    path('new_guarantee/', views.new_guarantee, name='new_guarantee'),
    path('new_guarantee_from_mainpage/', views.new_guarantee_from_mainpage, name='new_guarantee_from_mainpage'),
    path('costs_by_hand/', views.costs_by_hand, name='costs_by_hand'),
    path('receipt_site/<int:receipt_id>', views.receipt_site, name='receipt_site'),
    path('guarantee_site/<int:guarantee_id>', views.guarantee_site, name='guarantee_site'),
    path('expense_site/<int:expense_id>', views.expense_site, name='expense_site'),
    path('expenses_page/', views.expenses_page, name='expenses_page'),
    path('receipt_by_hand/', views.receipt_by_hand, name='receipt_by_hand'),
    path('receipts_page/', views.receipts_page, name='receipts_page'),
    path('receipt_settings/', views.receipt_settings, name='receipt_settings'),
    path('expense_settings/', views.expense_settings, name='expense_settings'),
    path('guarantee_settings/', views.guarantee_settings, name='guarantee_settings'),
    path('<int:expense_id>/edit_expense/', views.edit_expense, name='edit_expense'),
    path('<int:guarantee_id>/edit_guarantee/', views.edit_guarantee, name='edit_guarantee'),
    path('<int:guarantee_id>/elongate_guarantee/', views.elongate_guarantee, name='elongate_guarantee'),
    path('<int:receipt_id>/edit_receipt/', views.edit_receipt, name='edit_receipt'),
    path('<int:receipt_id>/delete_receipt/', views.delete_receipt, name='delete_receipt'),
    path('<int:expense_id>/delete_expense/', views.delete_expense, name='delete_expense'),
    path('<int:guarantee_id>/delete_guarantee/', views.delete_guarantee, name='delete_guarantee'),
    path('<int:receipt_id>/OCR_site/', views.OCR_site, name='OCR_site'),
    path('<int:receipt_id>/change_receipt_starred_status/', views.change_receipt_starred_status, name='change_receipt_starred_status'),
    path('<int:expense_id>/change_expense_starred_status/', views.change_expense_starred_status, name='change_expense_starred_status'),
    path('<int:receipt_id>/receipt_data_read/', views.receipt_data_read, name='receipt_data_read'),
    path('<int:receipt_id>/receipt_site_from_mainpage/', views.receipt_site_from_mainpage, name='receipt_site_from_mainpage'),
    path('<int:receipt_id>/<int:group_id>/receipt_site_from_grouppage/', views.receipt_site_from_grouppage, name='receipt_site_from_grouppage'),
    path('<int:expense_id>/expense_site_from_mainpage/', views.expense_site_from_mainpage, name='expense_site_from_mainpage'),
    path('<int:expense_id>/<int:group_id>/expense_site_from_grouppage/', views.expense_site_from_grouppage, name='expense_site_from_grouppage'),
    path('<int:guarantee_id>/guarantee_site_from_mainpage/', views.guarantee_site_from_mainpage, name='guarantee_site_from_mainpage'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)