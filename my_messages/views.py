from django.shortcuts import render
from .models import Message
# Create your views here.


def messages(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-date_created')
    context = {'messages':messages}
    return render(request, 'my_messages/messages.html', context)


def message_inside(request, message_id):
    message = Message.objects.get(id=message_id)
    message.new = False
    message.save()
    context = {'message': message}
    return render(request, 'my_messages/message_inside.html', context)