from django.shortcuts import render, redirect
from .models import Message, User
from groups.models import CommonGroups
from .forms import NewMessageForm
from django.template.defaultfilters import slugify
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import Http404
from profile_mangement.models import ProfileInfo


@login_required
def your_messages(request):
    all_messages = Message.objects.filter(receiver=request.user).order_by('-date_created')
    page_number = request.GET.get('page',1)

    for mes in all_messages:
        if not mes.is_seen_by_receiver and not mes.is_seen_by_sender:
            mes.delete()

    new = all_messages.filter(is_seen_by_receiver=True)

    p = Paginator(new, 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'all_messages': new, 'pages': pages, 'user': request.user}
    return render(request, 'my_messages/messages.html', context)


@login_required
def message_inside(request, message_id):
    message = Message.objects.get(id=message_id)

    if request.user != message.receiver and request.user != message.sender:
        return Http404

    if request.user.username == message.receiver.username or request.user.username == message.sender.username:
        if request.user.username == message.receiver.username:
            message.new = False

        message.save()
        context = {'message': message, 'user': request.user}
        return render(request, 'my_messages/message_inside.html', context)
    else:
        return Http404


@login_required
def message_sent(request):
    all_messages = Message.objects.filter(sender=request.user, group=None).order_by('-date_created')
    page_number = request.GET.get('page',1)

    for mes in all_messages:
        if not mes.is_seen_by_receiver and not mes.is_seen_by_sender:
            mes.delete()

    new = all_messages.filter(is_seen_by_sender=True)

    p = Paginator(new, 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)



    context = {'all_messages': new, 'pages': pages}
    return render(request, 'my_messages/message_sent.html', context)


@login_required
def new_message(request):
    if request.method == 'POST':
        form_temp = NewMessageForm(data=request.POST)
        req_temp = request.POST.copy()
        filtr = User.objects.filter(username=form_temp.data['receiver'])
        if filtr:
            req_temp.update({'receiver': filtr[0]})
            prof = ProfileInfo.objects.get(user=filtr[0])
            if request.user in prof.blocked_users.all():
                messages.error(request, "Nie można wysłać wiadomości - użytkownik Cię zablokował.")
                form = NewMessageForm(req_temp)
                context = {'form': form, 'user': request.user}
                return render(request, 'my_messages/new_message.html', context)
        else:
            req_temp.update({'receiver': filtr})
        form = NewMessageForm(req_temp)

        if form.is_valid():
            new_mes = form.save(commit=False)
            new_mes.sender = request.user
            new_mes.save()

            messages.success(request, "Wiadomość została wysłana.")
            return redirect('my_messages:your_messages')
        else:
            messages.error(request, "Wystąpił błąd podczas wysyłania wiadomości.")
    else:
        form = NewMessageForm()

    context = {'form': form, 'user': request.user}
    return render(request, 'my_messages/new_message.html', context)


@login_required
def member_accepted(request, message_id):
    message = Message.objects.get(id=message_id)
    group = CommonGroups.objects.get(id=message.group.id)
    profile = ProfileInfo.objects.get(user=message.sender)
    if profile.messages_by_groups:
        if group.number_of_members < group.max_number_of_members and message.sender not in group.members.all():
            group.members.add(message.sender)
            group.number_of_members += 1
            group.save()

            new_message = Message()
            new_message.sender = request.user
            new_message.receiver = message.sender

            new_message.title = "Gratulacje! Dołączyłeś do grupy " + group.group_name
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Od dzisiaj jesteś członkiem grupy " + group.group_name + "."
            new_message.message_type = "request_accepted"
            new_message.group = group
            new_message.save()

            messages.success(request, 'Wiadomość została wysłana.')
            message.answered = True
            message.save()
            return redirect('groups:groups')
        else:
            messages.error(request, 'Nie można dodać członka!')
            return redirect('my_messages:your_messages')
    else:
        messages.error(request, 'Użytkownik zablokował otrzymywanie wiadomości od grup.')
        return redirect('my_messages:your_messages')


@login_required
def membership_accepted(request, message_id):
    message = Message.objects.get(id=message_id)
    group = CommonGroups.objects.get(id=message.group.id)
    profile = ProfileInfo.objects.get(user=message.sender)
    if profile.messages_by_groups:
        if group.number_of_members < group.max_number_of_members and message.receiver not in group.members.all():
            group.members.add(message.sender)
            group.number_of_members += 1
            group.save()
            new_message = Message()
            new_message.sender = request.user
            new_message.receiver = message.sender

            new_message.title = "Użytkownik " + request.user + " dołączył do Twojej grupy " + group.group_name + "!"
            new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                               "Użytkownik " + request.user + " dołączył do Twojej grupy  " + group.group_name + "."
            new_message.message_type = "membership_accepted"
            new_message.group = group
            new_message.save()

            messages.success(request, 'Wiadomość została wysłana.')
            message.answered = True
            message.save()

            return redirect('groups:groups')
        else:
            messages.error(request, 'Nie można dołączyć z powodu braku miejsca w grupie! '
                                    'Skontaktuj się z właścicielem grupy w celu wyjaśnienia sytuacji.')
            return redirect('my_messages:your_messages')
    else:
        messages.error(request, 'Użytkownik zablokował otrzymywanie wiadomości od grup.')
        return redirect('my_messages:your_messages')


@login_required
def member_rejected(request, message_id):
    message = Message.objects.get(id=message_id)
    group = CommonGroups.objects.get(id=message.group.id)
    profile = ProfileInfo.objects.get(user=message.sender)
    if profile.messages_by_groups:
        new_message = Message()
        new_message.sender = request.user
        new_message.receiver = message.sender

        new_message.title = "Prośba o dołączenie do grupy " + group.group_name + " została odrzucona."
        new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                           "Niestety, Twoja prośna o przyjęcie do grupy " + group.group_name + " została odrzucona przez jej właściciela."
        new_message.message_type = "request_rejected"
        new_message.group = group
        new_message.save()

        messages.success(request, 'Wiadomość została wysłana.')
        message.answered = True
        message.save()

        return redirect('my_messages:your_messages')
    else:
        messages.error(request, 'Użytkownik zablokował otrzymywanie wiadomości od grup.')
        return redirect('my_messages:your_messages')


@login_required
def membership_rejected(request, message_id):
    message = Message.objects.get(id=message_id)
    group = CommonGroups.objects.get(id=message.group.id)
    profile = ProfileInfo.objects.get(user=message.sender)
    if profile.messages_by_groups:
        new_message = Message()
        new_message.sender = request.user
        new_message.receiver = message.sender

        new_message.title = "Użytkownik " + request.user.username + " odrzucił zaproszenie do grupy " + group.group_name
        new_message.text = "Witaj " + new_message.receiver.username + "!\n" + \
                           "Niestety, użytkownik, którego zaprosiłeś do grupy " + group.group_name + " odrzucił Twoje zaproszenie."
        new_message.message_type = "membership_rejected"
        new_message.group = group
        new_message.save()

        messages.success(request, 'Wiadomość została wysłana.')
        message.answered = True
        message.save()

        return redirect('my_messages:your_messages')
    else:
        messages.error(request, 'Użytkownik zablokował otrzymywanie wiadomości od grup.')
        return redirect('my_messages:your_messages')

@login_required
def delete_messages(request):
    if request.method == 'POST':
        keys = list(request.POST.keys())[1:]
        for key_id in keys:
            mes = Message.objects.get(id=int(key_id))
            if request.user == mes.sender:
                mes.is_seen_by_sender = False
            elif request.user == mes.receiver:
                mes.is_seen_by_receiver = False
            mes.save()
        return redirect("my_messages:your_messages")


@login_required
def delete_sent_messages(request):
    if request.method == 'POST':
        keys = list(request.POST.keys())[1:]
        for key_id in keys:
            Message.objects.get(id=int(key_id)).delete()
        return redirect("my_messages:message_sent")


@login_required
def message_settings(request):
    profile = ProfileInfo.objects.get(id=request.user.id)
    num = profile.blocked_users.count()
    context = {'user': request.user, 'profile': profile, "blocked_number": num}
    return render(request, 'my_messages/message_settings.html', context)


@login_required
def answer_message(request, message_id):
    message = Message.objects.get(id=message_id)
    profile = ProfileInfo.objects.get(user=message.sender)
    if profile.messages_by_users:
        if request.user != message.receiver:
            return Http404

        if request.method == 'POST':
            form = NewMessageForm(data=request.POST,
                                  initial={"receiver": message.sender, "title": "Re: " + message.title[:297]})
            prof = ProfileInfo.objects.get(user=message.sender)
            if request.user in prof.blocked_users.all():
                messages.error(request, "Wystąpił błąd podczas wysyłania wiadomości.")
                context = {'form': form, 'user': request.user, 'message': message}
                return render(request, 'my_messages/answer_message.html', context)
            if form.is_valid():
                new_mes = form.save(commit=False)
                new_mes.sender = request.user
                new_mes.save()
                messages.success(request, "Wiadomość została wysłana.")
                return redirect('my_messages:your_messages')
            else:
                messages.error(request, "Wystąpił błąd podczas wysyłania wiadomości.")
        else:
            form = NewMessageForm(initial={"receiver": message.sender.username, "title": "Re: " + message.title[:297],
                                           "text": "\n= = = = = = = = = =\n" + message.sender.username + " napisał:\n" + message.text})
    else:
        form = NewMessageForm(initial={"receiver": message.sender.username, "title": "Re: " + message.title[:297],
                                       "text": "\n= = = = = = = = = =\n" + message.sender.username + " napisał:\n" + message.text})
        messages.error(request, "Nie można wysłać wiadomości - użytkownik Cię zablokował.")

    context = {'form': form, 'user': request.user, 'message': message }
    return render(request, 'my_messages/answer_message.html', context)


@login_required
def del_all_messages(request):
    context = {'user': request.user}
    return render(request, 'my_messages/del_all_messages.html', context)


@login_required
def delete_all(request):
    messages_sent = Message.objects.filter(sender=request.user)
    messages_received = Message.objects.filter(receiver=request.user)

    for ms in messages_sent:
        ms.is_seen_by_sender = False
        ms.save()

    for mr in messages_received:
        mr.is_seen_by_receiver = False
        mr.save()

    return redirect("my_messages:your_messages")


@login_required
def block_options(request):
    profile = ProfileInfo.objects.get(id=request.user.id)
    if request.method == 'POST':
        if request.POST['block_radio'] == 'users':
            profile.messages_by_users = False
            profile.messages_by_groups = True
        elif request.POST['block_radio'] == 'groups':
            profile.messages_by_users = True
            profile.messages_by_groups = False
        elif request.POST['block_radio'] == 'groups_users':
            profile.messages_by_users = False
            profile.messages_by_groups = False
        else:
            profile.messages_by_groups = True
            profile.messages_by_users = True
        profile.save()
        messages.success(request, "Zmieniono ustawienie blokowania.")

    return redirect("my_messages:message_settings")


@login_required
def black_list(request):
    profile = ProfileInfo.objects.get(id=request.user.id)
    page_number = request.GET.get('page', 1)
    p = Paginator(profile.blocked_users.all(), 5)

    try:
        pages = p.page(page_number)
    except PageNotAnInteger:
        pages = p.page(1)
    except EmptyPage:
        pages = p.page(p.num_pages)

    context = {'user': request.user, 'banned': profile.blocked_users, 'pages': pages}
    return render(request, 'my_messages/black_list.html', context)


@login_required
def unban(request, user_id):
    user_unbanned = User.objects.get(id=user_id)
    profile = ProfileInfo.objects.get(id=request.user.id)
    profile.blocked_users.remove(user_unbanned)
    messages.success(request, f"Usunięto użytkownika {user_unbanned} z listy.")
    return redirect("my_messages:black_list")


@login_required
def add_to_blacklist(request):
    if request.method == "POST":
        try:
            u = User.objects.get(username=request.POST['user_to_ban'])
            user = User.objects.get(id=u.id)
            profile = ProfileInfo.objects.get(id=request.user.id)
            if user in profile.blocked_users.all():
                messages.error(request, "Użytkownik jest już na liście.")
            else:
                profile.blocked_users.add(user)
                messages.success(request, f"Pomyślnie dodano użytkownika.")
        except:
            messages.error(request, "Nie ma takiego użytkownika.")
    return redirect("my_messages:black_list")