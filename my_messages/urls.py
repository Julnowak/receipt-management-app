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
    path('<int:message_id>/', views.message_inside, name='message_inside'),
    path('delete_messages/', views.delete_messages, name='delete_messages'),
    path('del_all_messages/', views.del_all_messages, name='del_all_messages'),
    path('delete_all/', views.delete_all, name='delete_all'),
    path('black_list/', views.black_list, name='black_list'),
    path('unban/<int:user_id>', views.unban, name='unban'),
    path('add_to_blacklist/', views.add_to_blacklist, name='add_to_blacklist'),
    path('block_options/', views.block_options, name='block_options'),
    path('delete_sent_messages/', views.delete_sent_messages, name='delete_sent_messages'),
    path('message_settings/', views.message_settings, name='message_settings'),
    path('answer_message/<int:message_id>/', views.answer_message, name='answer_message'),
]