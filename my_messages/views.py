from django.shortcuts import render, redirect
from .models import Message,User
from .forms import NewMessageForm
from django.template.defaultfilters import slugify
# Create your views here.


def messages(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-date_created')
    context = {'messages': messages}
    return render(request, 'my_messages/messages.html', context)


def message_inside(request, message_id):
    message = Message.objects.get(id=message_id)
    message.new = False
    message.save()
    context = {'message': message}
    return render(request, 'my_messages/message_inside.html', context)


def message_sent(request):
    messages = Message.objects.filter(sender=request.user, group=None).order_by('-date_created')
    context = {'messages': messages}
    return render(request, 'my_messages/message_sent.html', context)


def new_message(request):
    try:
        mes_last_id = Message.objects.latest('id').id
    except:
        mes_last_id = 0

    if request.method == 'POST':
        form_temp = NewMessageForm(data=request.POST)
        req_temp = request.POST.copy()
        req_temp.update({'receiver': User.objects.get(username=form_temp.data['receiver'])})
        form = NewMessageForm(req_temp)

        if form.is_valid():
            new_mes = form.save(commit=False)
            new_mes.sender = request.user
            new_mes.slug = slugify(new_mes.title + " " + str(mes_last_id + 1))
            new_mes.save()
            return redirect('my_messages:my_messages')
    else:
        form = NewMessageForm()

    context = {'form': form}
    return render(request, 'my_messages/new_message.html', context)