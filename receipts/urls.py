from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'receipts'
urlpatterns = [
    path('', views.your_receipts, name='your_receipts'),
    path('new_receipt/', views.new_receipt, name='new_receipt'),
    path('costs_by_hand/', views.costs_by_hand, name='costs_by_hand'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)