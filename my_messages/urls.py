from django.urls import path, include
from . import views

app_name = 'my_messages'
urlpatterns = [
    path('', views.messages, name='my_messages'),
    path('<int:message_id>/', views.message_inside, name='message_inside')
]