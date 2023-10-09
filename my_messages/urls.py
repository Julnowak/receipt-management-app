from django.urls import path, include
from . import views

app_name = 'my_messages'
urlpatterns = [
    path('', views.your_messages, name='your_messages'),
    path('sent/', views.message_sent, name='message_sent'),
    path('member_accepted/<int:message_id>/', views.member_accepted, name='member_accepted'),
    path('member_rejected/<int:message_id>/', views.member_rejected, name='member_rejected'),
    path('membership_accepted/<int:message_id>/', views.membership_accepted, name='membership_accepted'),
    path('membership_rejected/<int:message_id>/', views.membership_rejected, name='membership_rejected'),
    path('new_message/', views.new_message, name='new_message'),
    path('<int:message_id>/', views.message_inside, name='message_inside')
]