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
    path('costs_by_hand/', views.costs_by_hand, name='costs_by_hand'),
    path('receipt_site/<int:receipt_id>', views.receipt_site, name='receipt_site'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)