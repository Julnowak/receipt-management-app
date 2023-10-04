from django.shortcuts import render, redirect
from .models import CommonGroups, User
from groups.forms import CommonGroupsForm
from django.contrib import messages

# Create your views here.


def groups(request):
    your_groups = CommonGroups.objects.filter(owner=request.user)
    member_of_groups = CommonGroups.objects.filter(members=request.user)
    context = {'your_groups': your_groups, "member_of_groups":member_of_groups}
    return render(request, 'groups/your_groups.html', context)


def group_site(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    members = group.members.all()
    user = request.user
    context = {"group": group, "members": members, "user": user}
    return render(request, 'groups/group_site.html', context)


def invite_page(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    context = {"group": group, "code": group.password}
    return render(request, 'groups/invite_page.html', context)


def search(request, group_id):
    text = 'noOne'
    group = CommonGroups.objects.get(id=group_id)
    if request.method == 'POST':
        name = request.POST.get('textfield', None)
        try:
            user = User.objects.get(username=name)
            #do something with user

            if group.number_of_members >= group.max_number_of_members:
                text = "Osiągnięto limit członków grupy"
            else:
                text = user
                group.number_of_members = group.number_of_members + 1
                group.members.add(user)
                group.save()

        except User.DoesNotExist:
            text = "Nie ma takiego użytkownika"

    context = {'text': text, 'group': group}
    return render(request, 'groups/search.html', context)

    # context = {"group": group, "code": group.password,'form': form}
    # return render(request, 'groups/invite_page.html', context)


def leaving_group_page(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    if request.method == 'POST':
        name = request.POST.get('textfield', None)

    context = {"group": group, "user": request.user}
    return render(request, 'groups/leaving_group_page.html', context)


# TO DO
def add_group(request):
    if request.method == 'POST':
        form = CommonGroupsForm(request.POST)

        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.owner = request.user
            new_group.save()
            new_group.members.add(request.user)
            messages.success(request, 'Grupa została utworzona')
            return redirect('groups:groups')
    else:
        form = CommonGroupsForm()

    names = list(form._meta.labels.values())
    group_name = names[0]
    max_members = names[1]
    pswd = names[2]
    context = {'form': form, 'group_name': group_name, 'max_members': max_members, 'password': pswd}
    return render(request, 'groups/add_group.html', context)

####
def delete_group(request,group_id):
    deletion(group_id)
    return redirect('groups:groups')

def deletion(group_id):
    group = CommonGroups.objects.get(id=group_id)
    group.delete()

### TO DO
def left_group(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    user = request.user
    if group.number_of_members == 1:
        deletion(group_id)
    else:
        group.members.remove(user)
        group.number_of_members -= 1
        group.save()

    return redirect('groups:groups')


def manage_group(request, group_id):
    group = CommonGroups.objects.get(id=group_id)
    delete_member_fun = delete_member_from_group
    context = {"group": group, "user": request.user, 'members': group.members.all(), "delete_member_fun": delete_member_fun}
    return render(request, 'groups/manage_group.html', context)


def search_group(request):
    groups_searched = 'None'
    number = 0
    exists = False
    if request.method == 'POST':
        group_name = request.POST.get('q')

        try:
            groups_searched = CommonGroups.objects.filter(group_name__icontains=group_name)
            number = CommonGroups.objects.filter(group_name__icontains=group_name).count()
            exists = True
        except :
            groups_searched = "Nie ma takiej grupy"

    context = {"user": request.user, 'exists': exists, 'groups': groups_searched, 'number': number}
    return render(request, 'groups/search_group.html', context)


def delete_member_from_group(member,group_id):
    group = CommonGroups.objects.get(id=group_id)
    group.members.remove(member)
    group.save()



