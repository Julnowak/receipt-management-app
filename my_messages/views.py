from django.shortcuts import render, redirect
from .models import Message, User
from groups.models import CommonGroups
from .forms import NewMessageForm
from django.template.defaultfilters import slugify
from django.contrib import messages
# Create your views here.


def your_messages(request):
    all_messages = Message.objects.filter(receiver=request.user).order_by('-date_created')
    context = {'all_messages': all_messages}
    return render(request, 'my_messages/messages.html', context)


def message_inside(request, message_id):
    message = Message.objects.get(id=message_id)
    message.new = False
    message.save()
    context = {'message': message}
    return render(request, 'my_messages/message_inside.html', context)


def message_sent(request):
    all_messages = Message.objects.filter(sender=request.user, group=None).order_by('-date_created')
    context = {'all_messages': all_messages}
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
            return redirect('my_messages:your_messages')
    else:
        form = NewMessageForm()

    context = {'form': form}
    return render(request, 'my_messages/new_message.html', context)


def member_accepted(request, message_id):
    message = Message.objects.get(id=message_id)

    group = CommonGroups.objects.get(id=message.group.id)
    if group.number_of_members < group.max_number_of_members and message.sender not in group.members.all():
        group.members.add(message.sender)
        group.number_of_members += 1
        group.save()

        try:
            mes_last_id = Message.objects.latest('id').id
        except:
            mes_last_id = 0

        new_message = Message()
        new_message.sender = request.user
        new_message.receiver = message.sender

        new_message.title = "Gratulacje! Dołączyłeś " + group.group_name
        new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
        new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                           "Od dzisiaj jesteś członkiem grupy " + group.group_name + "."
        new_message.message_type = "request_accepted"
        new_message.group = group
        new_message.save()

        messages.success(request, 'Wiadomość została wysłana.')

        return redirect('groups:groups')
    else:
        messages.error(request, 'Nie można dodać członka!')
        return redirect('my_messages:your_messages')


def membership_accepted(request, message_id):
    message = Message.objects.get(id=message_id)
    group = CommonGroups.objects.get(id=message.group.id)
    if group.number_of_members < group.max_number_of_members and message.receiver not in group.members.all():
        group.members.add(message.sender)
        group.number_of_members += 1
        group.save()

        try:
            mes_last_id = Message.objects.latest('id').id
        except:
            mes_last_id = 0

        new_message = Message()
        new_message.sender = request.user
        new_message.receiver = message.sender

        new_message.title = "Użytkownik " + request.user + " dołączył do Twojej grupy " + group.group_name + "!"
        new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
        new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                           "Użytkownik " + request.user + " dołączył do Twojej grupy  " + group.group_name + "."
        new_message.message_type = "membership_accepted"
        new_message.group = group
        new_message.save()

        messages.success(request, 'Wiadomość została wysłana.')

        return redirect('groups:groups')
    else:
        messages.error(request, 'Nie można dołączyć z powodu braku miejsca w grupie! '
                                'Skontaktuj się z właścicielem grupy w celu wyjaśnienia sytuacji.')
        return redirect('my_messages:your_messages')


def member_rejected(request, message_id):
    message = Message.objects.get(id=message_id)

    group = CommonGroups.objects.get(id=message.group.id)

    try:
        mes_last_id = Message.objects.latest('id').id
    except:
        mes_last_id = 0

    new_message = Message()
    new_message.sender = request.user
    new_message.receiver = message.sender

    new_message.title = "Prośba o dołączenie do grupy " + group.group_name + " została odrzucona."
    new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
    new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                       "Niestety, Twoja prośna o przyjęcie do grupy " + group.group_name + " została odrzucona przez jej właściciela."
    new_message.message_type = "request_rejected"
    new_message.group = group
    new_message.save()

    messages.success(request, 'Wiadomość została wysłana.')

    return redirect('my_messages:your_messages')


def membership_rejected(request, message_id):
    message = Message.objects.get(id=message_id)

    group = CommonGroups.objects.get(id=message.group.id)

    try:
        mes_last_id = Message.objects.latest('id').id
    except:
        mes_last_id = 0

    new_message = Message()
    new_message.sender = request.user
    new_message.receiver = message.sender

    new_message.title = "Użytkownik " + request.user.username + " odrzucił zaproszenie do grupy " + group.group_name
    new_message.slug = slugify(new_message.title + " " + str(mes_last_id + 1))
    new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                       "Niestety, użytkownik, którego zaprosiłeś do grupy " + group.group_name + " odrzucił Twoje zaproszenie."
    new_message.message_type = "membership_rejected"
    new_message.group = group
    new_message.save()

    messages.success(request, 'Wiadomość została wysłana.')

    return redirect('my_messages:your_messages')