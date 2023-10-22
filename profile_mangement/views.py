from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ProfileInfo, Icon, User
import datetime
from django.http import Http404
from django.contrib import messages
from django.core import validators
# Create your views here.


@login_required
def profile_management_site(request):
    try:
        my_profile = ProfileInfo.objects.get(user=request.user)
    except:
        my_profile = ProfileInfo.objects.create(user=request.user)

    if my_profile.user != request.user:
        return Http404

    age = datetime.date.today().year - my_profile.date_of_birth.year

    have_birthday = (datetime.date.today().month == my_profile.date_of_birth.month) and \
                    (datetime.date.today().day == my_profile.date_of_birth.day)

    picture = my_profile.profile_image
    if picture:
        img = picture.icon_code[:47] + '128" ' + picture.icon_code[51:59] + '128" ' + 'style="display:inline; vertical-align: middle;"' + picture.icon_code[62:]
    else:
        img = None
    context = {'img':img, 'user': request.user, "my_profile": my_profile, "age": age, 'have_birthday': have_birthday}
    return render(request, "profile_management/profile_management_site.html", context)


@login_required
def account_deletion(request):
    return render(request, "profile_management/account_deletion.html")


@login_required
def deletion(request):
    User.objects.get(id=request.user.id).delete()
    return redirect("homepage")


@login_required
def profile_showcase(request, member_id):
    try:
        my_profile = ProfileInfo.objects.get(user=member_id)
    except:
        my_profile = ProfileInfo.objects.filter(user=member_id)
    user = User.objects.get(id=member_id)
    age = datetime.date.today().year - my_profile.date_of_birth.year

    have_birthday = (datetime.date.today().month == my_profile.date_of_birth.month) and \
                    (datetime.date.today().day == my_profile.date_of_birth.day)

    picture = my_profile.profile_image
    if picture:
        img = picture.icon_code[:47] + '128" ' + picture.icon_code[51:59] + '128" ' + 'style="display:inline; vertical-align: middle;"' + picture.icon_code[62:]
    else:
        img = None

    context = {'img':img, 'user': user, "my_profile": my_profile, "age": age, 'have_birthday': have_birthday}
    return render(request, "profile_management/profile_showcase.html", context)


@login_required
def change_visibility(request):
    my_profile = ProfileInfo.objects.get(user=request.user)
    if my_profile.is_public:
        my_profile.is_public = False
    else:
        my_profile.is_public = True

    my_profile.save()
    return redirect("profile_management_site")


@login_required
def change_description(request):
    my_profile = ProfileInfo.objects.get(user=request.user)

    if request.method == "POST":
        my_profile.text = request.POST['description']
        my_profile.save()
        messages.success(request, 'Opis został zmieniony.')
        return redirect('profile_management_site')

    context = {'my_profile': my_profile}
    return render(request,"profile_management/change_description.html", context)


@login_required
def change_email(request):
    my_profile = ProfileInfo.objects.get(user=request.user)

    if request.method == "POST":
        try:
            validators.validate_email(request.POST["new_email"])
        except:
            messages.error(request, 'Coś poszło nie tak.')
            return redirect("profile_management_site")

        my_profile.email = request.POST["new_email"]
        my_profile.save()
        messages.success(request, 'Email został zmieniony.')
    return redirect("profile_management_site")


@login_required
def change_image(request):
    my_profile = ProfileInfo.objects.get(user=request.user)
    icons = Icon.objects.all()
    if request.method == "POST":
        my_profile.profile_image_background_color = request.POST["back_color"]
        my_profile.profile_image_color = request.POST["icon_color"]
        try:
            picture = Icon.objects.get(id=int(request.POST["profile_img"]))
            my_profile.profile_image = picture
        except:
            my_profile.profile_image = None
        my_profile.save()
        messages.success(request, 'Obraz został zmieniony.')
        return redirect("profile_management_site")
        return redirect("profile_management_site")

    context = {'my_profile': my_profile, 'icons': icons}
    return render(request,"profile_management/change_image.html", context)


@login_required
def change_name(request):
    if request.method == "POST":
        if len(request.POST['new_username']) < 3:
            messages.error(request, 'Coś poszło nie tak.')
            return redirect("profile_management_site")
        else:
            request.user.username = request.POST['new_username']
            request.user.save()
            messages.success(request, 'Nazwa użytkownika została zmieniona.')
    return redirect("profile_management_site")

