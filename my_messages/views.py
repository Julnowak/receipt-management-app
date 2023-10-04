from django.shortcuts import render

# Create your views here.


def messages(request):
    return render(request, 'my_messages/messages.html')